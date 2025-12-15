export type ROCIdent = string;
export type VesselIdent = string;

export enum Readiness {
    UNCERTAIN = 0,
    READY,
    ABORTED,
    ALIVE
}

export class ROC {
    id: ROCIdent;
    readiness: Readiness = Readiness.UNCERTAIN;
    controlledVessels: VesselIdent[] = [];

    constructor(id: ROCIdent) {
        this.id = id;
    }
}

export var thisRoc: ROC;
export function setThisRoc(roc: ROC) {
    thisRoc = roc;
}