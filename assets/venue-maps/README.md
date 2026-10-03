# Venue map integration

Add `/assets/venue-maps.css` as a stylesheet and `/assets/venue-maps.js` as a deferred script. Place `<div data-venue-map="boston-common-frog-pond"></div>` between arrival and facilities. Other IDs include `llbean-freeport`, `wells-beach`, `lifetime-burlington`. Favorite-place slug aliases and calendar venue names are accepted. For newly inserted calendar markup, call `window.AUsomeVenueMaps.mount(container)` after it is inserted.

No external map loads, location request, tracking or dependency. Offline printing is best done after loading the standalone print page. The component fetches one same-origin JSON file and has a retry fallback. Do not remove the visible route limitation, OSM credit or source links. 

## Coverage
48 venue records from 29 Favorite Places and 19 calendar venue profiles. One custom geographic landmark map (Frog Pond); current official map links for L.L.Bean and Wells; source-checked arrival questions for Life Time. Other records explicitly say mapping is unverified. An inventory record is not a completed access map.

## Source and rights record
Frog Pond base geometry retrieved from the public OpenStreetMap API on October 3, 2026. Original simplified SVG rendering; no map tiles, screenshots, venue photographs, artwork or logos copied. Extracted source geometry is distributed in `frog-pond-map-data.geojson` under ODbL 1.0 with source IDs, attribution and license URL. © OpenStreetMap contributors: https://www.openstreetmap.org/copyright . SVG map attribution remains visible; print notes include full attribution URL.

Official Boston maps were inspected for factual landmark relationships only. No city map artwork is reproduced. Official venue PDF maps are linked at the original publisher, not copied/rehosted. L.L.Bean links are the current September 2026 re-opening maps, not the older construction maps. Every facility claim in JSON has `sourceIds`; unmapped access routes, quiet spaces, changing equipment and unspecified toilet location are explicitly unknown. OSM accessibility tags were not treated as verified accessibility facts.

Future maps should record exact source URLs and review dates, facilities and routes separately, step-free-route verification, and rights basis. Never use generated artwork as geographic evidence. Keep seasonal operations and future improvements distinct from current facilities.
