import { map, latLng, tileLayer, type MapOptions } from "leaflet";

const options: MapOptions = {
    center: latLng(60, 15),
    zoom: 4,
};

export function initializeMap() {
    const mapElem = document.getElementById("map-view");
    if (mapElem) {
        const mymap = map(mapElem, options);

        tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }).addTo(mymap);
    }
}