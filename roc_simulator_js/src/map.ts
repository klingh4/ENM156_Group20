import { map, latLng, tileLayer, type MapOptions, marker, type LatLngExpression, Map as LeafMap, Marker } from "leaflet";

import "leaflet/dist/leaflet.css";
import "leaflet/dist/images/layers.png";
import "leaflet/dist/images/layers-2x.png";
import "leaflet/dist/images/marker-icon.png";
import "leaflet/dist/images/marker-icon-2x.png";
import "leaflet/dist/images/marker-shadow.png";

let mymap: LeafMap;

let markers = new Map<string, Marker>();

const options: MapOptions = {
    center: latLng(30.001015, -39.998854),
    zoom: 17,
};

export function initializeMap() {
    const mapElem = document.getElementById("map-view");
    if (mapElem) {
        mymap = map(mapElem, options);

        tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }).addTo(mymap);
    }
}

export function createOrMoveMarker(name: string, loc: LatLngExpression) {
    const m = markers.get(name);
    if (m) {
        // Move already existing
        m.setLatLng(loc);
    } else {
        // Create a new marker
        markers.set(name, marker(loc, { title: name }).addTo(mymap));
    }
}

export function deleteMarker(name: string) {
    const m = markers.get(name);
    if (m) {
        m.remove();
        markers.delete(name);
    }
}