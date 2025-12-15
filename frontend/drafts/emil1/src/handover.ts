import type { Sample } from "@eclipse-zenoh/zenoh-ts";
import { type VesselIdent, ROC, Readiness, type ROCIdent, thisRoc } from "./roc";
import { pubAbortHandover, pubAssertReady, publishRelinquish, publishTakeover } from "./zenoh-interfacer";

export type SafetyGateIdent = string;

export class Handover {
    #secondsUntilSafetyGate: number | undefined;
    gateId: SafetyGateIdent;
    vesselId: VesselIdent;
    hasVesselRequestedHandover: boolean = false;
    originallyResponsible: ROC;
    receivingResponsibility: ROC;
    timerElement: HTMLElement | undefined;
    handoverInitiated: boolean = false;
    takeoverIntervalId: number | undefined;
    handoverResult: string | null = null;

    // UI Elements for readiness
    origRocStatusElem: HTMLElement | null = null;
    recvRocStatusElem: HTMLElement | null = null;

    // UI Elements for result
    statusIndicatorsContainer: HTMLElement | null = null;
    resultContainer: HTMLElement | null = null;
    resultValueElem: HTMLElement | null = null;

    public set hasVesselRequestedHandoverValue(value: boolean) {
        this.hasVesselRequestedHandover = value;
        if (value) {
            setInterval(this.performHandoverIfAppropriate.bind(this), 1000);
        }
    }

    constructor(gate: SafetyGateIdent
        , vessel: VesselIdent
        , originallyResponsible: ROC
        , receivingResponsibility: ROC
        , linkButtons: boolean = false
        , linkTimer: boolean = false) {
        this.gateId = gate;
        this.vesselId = vessel;
        this.originallyResponsible = originallyResponsible;
        this.receivingResponsibility = receivingResponsibility;
        if (linkButtons) { this.linkControlButtons(); }
        if (linkTimer) { this.linkTimerElement(); }
    }

    setUIElements(
        origStatus: HTMLElement | null,
        recvStatus: HTMLElement | null,
        origLabel: HTMLElement | null,
        recvLabel: HTMLElement | null,
        indicatorsContainer: HTMLElement | null,
        resultContainer: HTMLElement | null,
        resultValue: HTMLElement | null
    ) {
        this.origRocStatusElem = origStatus;
        this.recvRocStatusElem = recvStatus;
        this.statusIndicatorsContainer = indicatorsContainer;
        this.resultContainer = resultContainer;
        this.resultValueElem = resultValue;

        if (origLabel) origLabel.innerText = `Original (${this.originallyResponsible.id})`;
        if (recvLabel) recvLabel.innerText = `Receiving (${this.receivingResponsibility.id})`;
        this.updateReadinessUI();
    }

    updateReadinessUI() {
        // If we have a result, don't update readiness indicators (they should be hidden)
        if (this.handoverResult) return;

        if (this.origRocStatusElem) this.updateRocBadge(this.origRocStatusElem, this.originallyResponsible.readiness);
        if (this.recvRocStatusElem) this.updateRocBadge(this.recvRocStatusElem, this.receivingResponsibility.readiness);
    }

    setHandoverResult(result: string) {
        this.handoverResult = result;

        // Hide readiness indicators
        if (this.statusIndicatorsContainer) {
            this.statusIndicatorsContainer.style.display = 'none';
        }

        // Show result container
        if (this.resultContainer && this.resultValueElem) {
            this.resultContainer.style.display = 'flex';
            this.resultValueElem.innerText = result;

            // Optional: color coding based on success/failure content
            if (result.toUpperCase().includes("COMPLETED") || result.toUpperCase().includes("SUCCESS")) {
                this.resultValueElem.style.color = "#059669"; // Green
            } else {
                this.resultValueElem.style.color = "#DC2626"; // Red (e.g., if aborted)
            }
        }

        // Also ensure timer stops if running
        if (this.takeoverIntervalId) {
            clearInterval(this.takeoverIntervalId);
            this.takeoverIntervalId = undefined;
        }
    }

    updateRocBadge(element: HTMLElement, readiness: Readiness) {
        element.className = 'status-badge'; // Reset classes
        switch (readiness) {
            case Readiness.READY:
                element.classList.add('status-ready');
                element.innerText = "READY";
                break;
            case Readiness.ABORTED:
                element.classList.add('status-aborted');
                element.innerText = "ABORTED";
                break;
            default:
                element.classList.add('status-uncertain');
                element.innerText = "UNCERTAIN";
                break;
        }
    }

    areBothReady(): boolean {
        return this.originallyResponsible.readiness === Readiness.READY &&
            this.receivingResponsibility.readiness === Readiness.READY;
    }

    getRocWithId(id: ROCIdent): ROC | undefined {
        if (this.originallyResponsible.id === id) {
            return this.originallyResponsible;
        } else if (this.receivingResponsibility.id === id) {
            return this.receivingResponsibility;
        } else {
            return undefined;
        }
    }

    getOtherRoc(id: ROCIdent): ROC | undefined {
        if (this.originallyResponsible.id === id) {
            return this.receivingResponsibility;
        } else if (this.receivingResponsibility.id === id) {
            return this.originallyResponsible;
        } else {
            return undefined;
        }
    }

    public set secondsUntilSafetyGate(seconds: number) {
        if (isNaN(seconds)) {
            return;
        }
        this.#secondsUntilSafetyGate = seconds;
        if (this.timerElement) {
            this.timerElement.innerText = seconds.toFixed(1);
        }
    }

    public get secondsUntilSafetyGate(): number | undefined {
        return this.#secondsUntilSafetyGate;
    }

    async receivedAssertion(sample: Sample) {
        let otherRoc = this.getOtherRoc(thisRoc.id);
        if (!otherRoc) {
            console.error("Received assertion for unknown ROC ID: " + otherRoc);
            return;
        }

        const assertion = sample.payload().toString();
        if (assertion.trim() === "READY") {
            console.log("The other ROC is READY.");
            if (otherRoc.readiness === Readiness.ABORTED) {
                console.error("Conflict: The other ROC had previously ABORTED but tried to become READY.");
            }
            else {
                otherRoc.readiness = Readiness.READY;
            }
        } else if (assertion.trim() === "ABORT") {
            console.log("The other ROC has ABORTED the handover.");
            otherRoc.readiness = Readiness.ABORTED;
        } else {
            console.warn("Received unknown assertion: " + assertion);
        }

        this.updateReadinessUI();
        this.performHandoverIfAppropriate();
    }

    performHandoverIfAppropriate() {
        if (this.handoverInitiated || this.handoverResult) { // Don't restart if done
            return;
        }

        console.log(`Readiness states - Originally responsible: ${this.originallyResponsible.readiness}, Receiving responsibility: ${this.receivingResponsibility.readiness}, Vessel requested handover: ${this.hasVesselRequestedHandover}`);
        if (this.areBothReady() && this.hasVesselRequestedHandover) {
            this.performHandover();
        }
    }

    performHandover() {
        if (!this.areBothReady()) {
            throw new Error("Cannot perform handover when both ROCs are not ready!");
        }

        this.handoverInitiated = true;
        console.log(`Performing handover of vessel ${this.vesselId} at safety gate ${this.gateId}...`);
        if (thisRoc.id === this.originallyResponsible.id) {
            this.#playRoleAsOriginallyResponsible();
        } else if (thisRoc.id === this.receivingResponsibility.id) {
            this.#playRoleAsReceivingResponsibility();
        } else {
            console.warn("This ROC is not involved in the handover!");
        }
    }

    #playRoleAsOriginallyResponsible() {
        console.log("Playing role as originally responsible ROC...");
        publishRelinquish();
    }

    #playRoleAsReceivingResponsibility() {
        console.log("Playing role as receiving responsibility ROC...");
        this.takeoverIntervalId = setInterval(() => {
            publishTakeover();
        }, 1000);
    }

    linkTimerElement() {
        const timeElem = document.getElementById("timer")
        if (timeElem) {
            this.timerElement = timeElem;
        }
    }

    // Link buttons to functions
    linkControlButtons() {
        const readyBtn = document.getElementById("btn-ready");
        if (readyBtn) {
            readyBtn.removeEventListener("click", this.assertReady.bind(this));
            readyBtn.addEventListener("click", this.assertReady.bind(this));
        }
        const abortBtn = document.getElementById("btn-abort");
        if (abortBtn) {
            abortBtn.removeEventListener("click", this.abortHandover.bind(this));
            abortBtn.addEventListener("click", this.abortHandover.bind(this));
        }
    }

    assertReady() {
        console.log("ASSERTING READY...");
        thisRoc.readiness = Readiness.READY;
        pubAssertReady();
        this.updateReadinessUI();
        this.performHandoverIfAppropriate();
    }

    abortHandover() {
        console.log("ABORTING HANDOVER...");
        thisRoc.readiness = Readiness.ABORTED;
        pubAbortHandover();
        this.updateReadinessUI();
    }
}