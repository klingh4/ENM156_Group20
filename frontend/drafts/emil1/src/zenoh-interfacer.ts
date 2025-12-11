import { Config, Session, Subscriber, type Sample, Encoding, Publisher } from "@eclipse-zenoh/zenoh-ts";
import { decodePayloadFromTypeName, uncover } from "@rise-maritime/keelson-js"
import type { LocationFix } from '@rise-maritime/keelson-js/dist/payloads/index.foxglove'
import type { TimestampedFloat } from '@rise-maritime/keelson-js/dist/payloads/Primitives';
import { createOrMoveMarker } from "./map";
import { type Handover } from "./handover";
import { Readiness, thisRoc, type ROCIdent, type VesselIdent } from "./roc";

const ZENOH_BRIDGE_REMOTE_API_DEFAULT_PORT = "10000";

let session: Session;
let assertionPublisher: Publisher;
let relinquishPublisher: Publisher;
let takeoverPublisher: Publisher;
let handoverRequestSubscriber: Subscriber;
let handoverStateSubscriber: Subscriber;

export async function connectToZenohNetwork(ipAddress: string = "localhost", port: string = ZENOH_BRIDGE_REMOTE_API_DEFAULT_PORT) {
    session = await Session.open(new Config(`ws://${ipAddress}:${port}`));
}

export async function StartListeningToVessel(vesselId: VesselIdent) {
    if (!session) {
        throw new Error("Zenoh session not established yet!");
    }

    await session.declareSubscriber(`rise/@v0/@v0/${vesselId}/pubsub/location_fix/gnss/0`, {
        handler: (sample: Sample) => {
            let p = uncover(sample.payload().toBytes())?.[2]
            if (p) {
                const loc = decodePayloadFromTypeName('foxglove.LocationFix', p) as LocationFix;
                createOrMoveMarker(loc.frameId, [loc.latitude, loc.longitude]);
            }

        }
    });
    const sogElem = document.getElementById("sog");
    if (sogElem)
        await session.declareSubscriber(`rise/@v0/@v0/${vesselId}/pubsub/speed_over_ground_knots/gnss/0`, {
            handler: (sample: Sample) => {
                let p = uncover(sample.payload().toBytes())?.[2]
                if (p) {
                    const sogVal = decodePayloadFromTypeName('keelson.TimestampedFloat', p) as TimestampedFloat;
                    sogElem.innerText = String(sogVal.value)
                }

            }
        });
    const cogElem = document.getElementById("cog");
    if (cogElem)
        await session.declareSubscriber(`rise/@v0/@v0/${vesselId}/pubsub/course_over_ground_deg/gnss/0`, {
            handler: (sample: Sample) => {
                let p = uncover(sample.payload().toBytes())?.[2]
                if (p) {
                    const cogVal = decodePayloadFromTypeName('keelson.TimestampedFloat', p) as TimestampedFloat;
                    cogElem.innerText = String(cogVal.value);
                }
            }
        });
};

export async function EstablishHandoverCommunication(thisRocId: ROCIdent, handover: Handover) {
    if (!session) {
        throw new Error("Zenoh session not established yet!");
    }
    if (assertionPublisher) {
        throw new Error("Handover communication already established!");
    }

    // Declare the assertion publisher
    assertionPublisher = await session.declarePublisher(`rise/@v0/${thisRocId}/pubsub/handover/assertion`, {
        encoding: Encoding.TEXT_PLAIN
    });

    // Declare the assertion subscriber
    const otherRoc = handover.getOtherRoc(thisRocId);
    if (!otherRoc) {
        throw new Error("Could not find the other ROC in the handover!");
    }
    await session.declareSubscriber(`rise/@v0/${otherRoc.id}/pubsub/handover/assertion`, {
        handler: (sample: Sample) => handover.receivedAssertion(sample)
    });

    // Subscribe to time updates
    await session.declareSubscriber(`rise/@v0/${handover.vesselId}/pubsub/remote_time/bridge/1`, {
        handler: (sample: Sample) => handover.secondsUntilSafetyGate = (parseFloat(sample.payload().toString()))
    });


    // Declare the relinquish publisher
    relinquishPublisher = await session.declarePublisher(`${handover.vesselId}/handover/relinquish`, {
        encoding: Encoding.TEXT_PLAIN
    });

    // Declare the takeover subscriber
    takeoverPublisher = await session.declarePublisher(`${handover.vesselId}/handover/takeover`, {
        encoding: Encoding.TEXT_PLAIN
    });

    // Declare the handover request subscriber
    handoverRequestSubscriber = await session.declareSubscriber(`rise/@v0/${handover.vesselId}/handover/request`, {
        handler: (sample: Sample) => {
            console.log("Received handover request: " + sample.payload().toString());
            if (sample.payload().toString().includes("READY_FOR_HANDOVER")) {
                console.log("Recognized vessels request for handover.");
                handover.hasVesselRequestedHandover = true;
                handover.performHandoverIfAppropriate();
            }
        }
    });


}

export async function pubAssertReady() {
    if (assertionPublisher) {
        await assertionPublisher.put("READY");
    } else {
        console.error("Assertion publisher not established yet!");
    }
}

export async function pubAbortHandover() {
    if (assertionPublisher) {
        await assertionPublisher.put("ABORT");
    } else {
        console.error("Assertion publisher not established yet!");
    }
}

export async function publishRelinquish() {
    if (relinquishPublisher) {
        console.log("PUBLISHING RELINQUISH...");
        await relinquishPublisher.put(thisRoc.id);
    } else {
        console.error("Relinquish publisher not established yet!");
    }
}

export async function publishTakeover() {
    if (takeoverPublisher) {
        console.log("PUBLISHING TAKEOVER...");
        await takeoverPublisher.put(thisRoc.id);
    } else {
        console.error("Takeover publisher not established yet!");
    }
}

export async function declareStateHandler(vesselId: VesselIdent, handler: (sample: Sample) => void) {
    if (!session) {
        throw new Error("Zenoh session not established yet!");
    }

    // Declare the handover state subscriber
    handoverStateSubscriber = await session.declareSubscriber(`rise/@v0/${vesselId}/handover/state`, {
        handler: handler
    });
}