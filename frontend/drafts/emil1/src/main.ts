import "./style.css"
import { StartListeningToVessel, EstablishHandoverCommunication, connectToZenohNetwork, declareStateHandler } from "./zenoh-interfacer"
import { activateRemarkResizing } from "./remark-resizing"
import { initializeMap } from "./map"
import { Handover } from "./handover"
import { ROC, setThisRoc, thisRoc } from "./roc"
import type { Sample } from "node_modules/@eclipse-zenoh/zenoh-ts/dist/sample"

// var thisRoc!: ROC;
let otherRoc!: ROC;
function promptForRocId() {
    let thisRocId: string | undefined = prompt("Enter this ROC's ID:") || undefined;
    while (!thisRocId) {
        thisRocId = prompt("What is this ROC's ID? It cannot be empty:") || undefined;
    }
    let otherRocId: string | undefined = prompt("Enter the other ROC's ID:") || undefined;
    while (!otherRocId) {
        otherRocId = prompt("What is the other ROC's ID? It cannot be empty:") || undefined;
    }
    setThisRoc(new ROC(thisRocId));
    otherRoc = new ROC(otherRocId);
    document.title = thisRoc.id || "";
    console.log("This ROC's ID is: " + (thisRoc.id || ""));
}

promptForRocId();
const handover = new Handover(
    "safety-gate-1",
    "MASS_0",
    thisRoc.id == "ROC_1" ? thisRoc : otherRoc,
    otherRoc.id == "ROC_1" ? thisRoc : otherRoc
);
const timeElem = document.getElementById("timer")
if (timeElem) {
    handover.timerElement = timeElem;
}

activateRemarkResizing();
initializeMap();
await connectToZenohNetwork();
await StartListeningToVessel(handover.vesselId);
await EstablishHandoverCommunication(thisRoc.id, handover);
declareStateHandler(handover.vesselId,
    ((sample: Sample) => {
        console.log("Received handover state update: " + sample.payload().toString());
        if (sample.payload().toString().includes("HANDOVER_COMPLETED")) {
            if (handover.takeoverIntervalId) {
                clearInterval(handover.takeoverIntervalId);
            }
        }
    }));
