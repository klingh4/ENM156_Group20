import { connect } from "./zenoh-interfacer"
import { activateRemarkResizing } from "./remark-resizing"
import { initializeMap } from "./map"

activateRemarkResizing();
initializeMap();
connect();