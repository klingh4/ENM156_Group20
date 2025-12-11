import "./style.css"
import { StartListeningToVessel, EstablishHandoverCommunication, connectToZenohNetwork, declareStateHandler, SubscribeToVesselTime } from "./zenoh-interfacer"
import { activateRemarkResizing } from "./remark-resizing"
import { initializeMap } from "./map"
import { Handover } from "./handover"
import { ROC, setThisRoc, thisRoc, Readiness } from "./roc"
import type { Sample } from "@eclipse-zenoh/zenoh-ts"

// Initialize UI elements immediately
activateRemarkResizing();
initializeMap();

// Dialog handling
const setupRocDialog = document.getElementById("setup-roc-dialog") as HTMLDialogElement;
const setupRocForm = document.getElementById("setup-roc-form") as HTMLFormElement;

const configHandoverDialog = document.getElementById("config-handover-dialog") as HTMLDialogElement;
const configHandoverForm = document.getElementById("config-handover-form") as HTMLFormElement;

// Handle JSON file upload for configuration
const handoverFileInput = document.getElementById("handover-file") as HTMLInputElement;
if (handoverFileInput) {
    handoverFileInput.addEventListener("change", (event) => {
        const file = handoverFileInput.files?.[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    const json = JSON.parse(e.target?.result as string);

                    const originalInput = document.getElementById("original-roc-id") as HTMLInputElement;
                    const receivingInput = document.getElementById("receiving-roc-id") as HTMLInputElement;
                    const vesselInput = document.getElementById("vessel-id") as HTMLInputElement;
                    const gateInput = document.getElementById("gate-id") as HTMLInputElement;

                    if (json.OriginallyResponsible) originalInput.value = json.OriginallyResponsible;
                    if (json.ReceivingResponsibility) receivingInput.value = json.ReceivingResponsibility;
                    if (json.Vessel) vesselInput.value = json.Vessel;
                    if (json.SafetyGate) gateInput.value = json.SafetyGate;

                } catch (error) {
                    console.error("Error parsing JSON:", error);
                    alert("Invalid JSON file.");
                }
            };
            reader.readAsText(file);
        }
    });
}

// Prevent closing by Escape key to ensure data entry
[setupRocDialog, configHandoverDialog].forEach(dialog => {
    if (dialog) {
        dialog.addEventListener("cancel", (event) => {
            event.preventDefault();
        });
    }
});

// Show the setup ROC modal on load
if (typeof setupRocDialog.showModal === "function") {
    // Ensure it's not already open as non-modal (standard HTML safety)
    if (setupRocDialog.open) {
        setupRocDialog.close();
    }
    setupRocDialog.showModal();
} else {
    alert("The <dialog> API is not supported by this browser");
}

// 1. Handle Setup ROC Submission
setupRocForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const formData = new FormData(setupRocForm);
    const thisRocId = formData.get("thisRocId") as string;

    if (thisRocId) {
        // Setup This ROC
        setThisRoc(new ROC(thisRocId));
        document.title = thisRoc.id;
        console.log(`Initialized: This ROC=${thisRoc.id}`);

        // Close setup dialog and open configuration dialog
        setupRocDialog.close();
        if (configHandoverDialog.open) configHandoverDialog.close();
        configHandoverDialog.showModal();
    }
});

// 2. Handle Handover Configuration Submission
configHandoverForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const formData = new FormData(configHandoverForm);
    const originalRocId = formData.get("originalRocId") as string;
    const receivingRocId = formData.get("receivingRocId") as string;
    const gateId = formData.get("gateId") as string;
    const vesselId = formData.get("vesselId") as string;

    if (originalRocId && receivingRocId && gateId && vesselId) {
        console.log(`Configuring Handover: Original ROC=${originalRocId}, Receiving ROC=${receivingRocId}, Gate=${gateId}, Vessel=${vesselId}`);

        const vesselTitleDisplay = document.getElementById("vessel-title-display");
        if (vesselTitleDisplay) vesselTitleDisplay.innerText = `${vesselId}`;

        // Initialize Handover Logic
        // Determine the ROC objects based on who is thisRoc
        // If thisRoc is the original, use it. Otherwise, create a new ROC for original.
        const originalRoc = thisRoc.id === originalRocId ? thisRoc : new ROC(originalRocId);

        // If thisRoc is the receiving, use it. Otherwise, create a new ROC for receiving.
        const receivingRoc = thisRoc.id === receivingRocId ? thisRoc : new ROC(receivingRocId);

        const handover = new Handover(
            gateId,
            vesselId,
            originalRoc,
            receivingRoc,
            true,  // linkButtons
            true   // linkTimer
        );

        // Setup UI references for status updates
        handover.setUIElements(
            document.getElementById("orig-roc-status"),
            document.getElementById("recv-roc-status"),
            document.getElementById("status-original-label"),
            document.getElementById("status-receiving-label")
        );

        // Update local button listeners to refresh UI
        const readyBtn = document.getElementById("btn-ready");
        const abortBtn = document.getElementById("btn-abort");

        if (readyBtn) {
            readyBtn.addEventListener("click", () => handover.updateReadinessUI());
        }
        if (abortBtn) {
            abortBtn.addEventListener("click", () => handover.updateReadinessUI());
        }

        // Close dialog
        configHandoverDialog.close();

        // Start Network Operations
        try {
            await connectToZenohNetwork();
            await StartListeningToVessel(handover.vesselId);

            // Subscribe to time for everyone (participants and observers)
            await SubscribeToVesselTime(handover.vesselId, (seconds) => {
                handover.secondsUntilSafetyGate = seconds;
            });

            // Only establish handover communication if this ROC is explicitly involved
            if (thisRoc.id === originalRoc.id || thisRoc.id === receivingRoc.id) {
                console.log(`This ROC (${thisRoc.id}) is a participant in the handover. Establishing communication.`);
                await EstablishHandoverCommunication(thisRoc.id, handover);
            } else {
                console.log(`This ROC (${thisRoc.id}) is NOT a participant in the handover (Original: ${originalRoc.id}, Receiving: ${receivingRoc.id}). Monitoring only.`);

                // Hide control buttons if not involved
                const btnReady = document.getElementById("btn-ready");
                const btnAbort = document.getElementById("btn-abort");
                if (btnReady) btnReady.style.display = 'none';
                if (btnAbort) btnAbort.style.display = 'none';
            }

            declareStateHandler(handover.vesselId, ((sample: Sample) => {
                console.log("Received handover state update: " + sample.payload().toString());
                if (sample.payload().toString().includes("HANDOVER_COMPLETED")) {
                    if (handover.takeoverIntervalId) {
                        clearInterval(handover.takeoverIntervalId);
                    }
                }
            }));
        } catch (error) {
            console.error("Failed to initialize Zenoh connection:", error);
            alert("Failed to connect to Zenoh network. Check console for details.");
        }
    }
});

// Configure button in control bar re-opens the handover configuration dialog
const configBtn = document.getElementById("btn-configure");
if (configBtn) {
    configBtn.addEventListener("click", () => {
        configHandoverDialog.showModal();
    });
}