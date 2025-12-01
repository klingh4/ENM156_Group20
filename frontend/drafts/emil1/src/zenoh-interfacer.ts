import { Config, Session, type Sample } from "@eclipse-zenoh/zenoh-ts";
import { decodePayloadFromTypeName, uncover } from "@rise-maritime/keelson-js"

const ZENOH_BRIDGE_REMOTE_API_DEFAULT_PORT = "10000";
const SUB_KEY = "rise/@v0/@v0/MASS_0/pubsub/location_fix/gnss/0"

console.log("Starting session...");
let session;
let subscriber;
export async function connect() {
    session = await Session.open(new Config("ws://localhost:" + ZENOH_BRIDGE_REMOTE_API_DEFAULT_PORT));
    subscriber = await session.declareSubscriber(SUB_KEY, {
        handler: (sample: Sample) => {
            console.log(`Recieved message of ${sample.encoding()} encoding`);
            let p = uncover(sample.payload().toBytes())?.[2]
            if (p) {
                const loc = decodePayloadFromTypeName('foxglove.LocationFix', p);
                console.log(loc);
            }

        }
    });
    console.log("Subscriber declared?");
}