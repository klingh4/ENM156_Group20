import { Config, Session, Subscriber, type Sample } from "@eclipse-zenoh/zenoh-ts";
import { decodePayloadFromTypeName, uncover } from "@rise-maritime/keelson-js"
import type { LocationFix } from '@rise-maritime/keelson-js/dist/payloads/index.foxglove'
import type { TimestampedFloat } from '@rise-maritime/keelson-js/dist/payloads/Primitives';
import { createOrMoveMarker } from "./map";

const ZENOH_BRIDGE_REMOTE_API_DEFAULT_PORT = "10000";
const SOG_KEY = "rise/@v0/@v0/MASS_0/pubsub/speed_over_ground_knots/gnss/0"
const COG_KEY = "rise/@v0/@v0/MASS_0/pubsub/course_over_ground_deg/gnss/0"
const LOCATION_FIX_KEY = "rise/@v0/@v0/MASS_0/pubsub/location_fix/gnss/0"

console.log("Starting session...");
let session;
let subscribers: Array<Subscriber> = [];
export async function connect() {
    session = await Session.open(new Config("ws://localhost:" + ZENOH_BRIDGE_REMOTE_API_DEFAULT_PORT));
    subscribers.push(await session.declareSubscriber(LOCATION_FIX_KEY, {
        handler: (sample: Sample) => {
            let p = uncover(sample.payload().toBytes())?.[2]
            if (p) {
                const loc = decodePayloadFromTypeName('foxglove.LocationFix', p) as LocationFix;
                createOrMoveMarker(loc.frameId, [loc.latitude, loc.longitude]);
            }

        }
    }));
    const sogElem = document.getElementById("sog");
    if (sogElem)
        subscribers.push(await session.declareSubscriber(SOG_KEY, {
            handler: (sample: Sample) => {
                let p = uncover(sample.payload().toBytes())?.[2]
                if (p) {
                    const sogVal = decodePayloadFromTypeName('keelson.TimestampedFloat', p) as TimestampedFloat;
                    sogElem.innerText = String(sogVal.value)
                }

            }
        }));
    const cogElem = document.getElementById("cog");
    if (cogElem)
        subscribers.push(await session.declareSubscriber(COG_KEY, {
            handler: (sample: Sample) => {
                let p = uncover(sample.payload().toBytes())?.[2]
                if (p) {
                    const cogVal = decodePayloadFromTypeName('keelson.TimestampedFloat', p) as TimestampedFloat;
                    cogElem.innerText = String(cogVal.value);
                }
            }
        }));
};