import { connect } from "./zenoh-interfacer"
import { activateRemarkResizing } from "./remark-resizing"
import { initializeMap } from "./map"

import "./style.css"

activateRemarkResizing();
initializeMap();
connect();