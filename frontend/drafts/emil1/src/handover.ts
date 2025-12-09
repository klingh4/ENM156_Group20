import type { Sample } from "node_modules/@eclipse-zenoh/zenoh-ts/dist/sample";
import { type VesselIdent, ROC, Readiness, type ROCIdent, thisRoc } from "./roc";
import { publishRelinquish, publishTakeover } from "./zenoh-interfacer";

export type SafetyGateIdent = string;

export class Handover {
    secondsUntilSafetyGate: number | undefined;
    gateId: SafetyGateIdent;
    vesselId: VesselIdent;
    hasVesselRequestedHandover: boolean = false;
    originallyResponsible: ROC;
    receivingResponsibility: ROC;
    timerElement: HTMLElement | undefined;
    handoverInitiated: boolean = false;
    takeoverIntervalId: number | undefined;

    public set hasVesselRequestedHandoverValue(value: boolean) {
        this.hasVesselRequestedHandover = value;
        if (value) {
            setInterval(this.performHandoverIfAppropriate.bind(this), 1000);
        }
    }

    constructor(gate: SafetyGateIdent, vessel: VesselIdent, originallyResponsible: ROC, receivingResponsibility: ROC) {
        this.gateId = gate;
        this.vesselId = vessel;
        this.originallyResponsible = originallyResponsible;
        this.receivingResponsibility = receivingResponsibility;
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

    updateTimeToGate(seconds: number) {
        if (isNaN(seconds)) {
            return;
        }
        this.secondsUntilSafetyGate = seconds;
        if (this.timerElement) {
            this.timerElement.innerText = seconds.toFixed(1);
        }
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

        this.performHandoverIfAppropriate();
    }

    performHandoverIfAppropriate() {
        if (this.handoverInitiated) {
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
        setInterval(() => {
            publishTakeover();
        }, 1000);
    }
}