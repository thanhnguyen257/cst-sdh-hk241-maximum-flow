var prevStartSelect = null;
var prevDestinationSelect = null;

function populateOptions() {
    fetch('/get_options')
        .then(response => response.json())
        .then(data => {
            const startSelect = document.getElementById('start');
            let idx = 0;
            data.start.forEach(option => {
                const opt = document.createElement('option');
                opt.textContent = idx+"."+option;
                opt.value = idx++;
                startSelect.appendChild(opt);
            });
            startSelect.addEventListener("change", function() {
                let mapDocument = document.getElementById("map-frame").contentDocument;
                if (prevStartSelect !== null && prevStartSelect !== prevDestinationSelect) {
                    mapDocument.querySelectorAll(".leaflet-marker-pane img")[prevStartSelect].src = "https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/images/marker-icon-2x.png";
                }
                mapDocument.querySelectorAll(".leaflet-marker-pane img")[this.value].src = "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png";
                prevStartSelect = this.value;
            });

            idx = 0
            const destinationSelect = document.getElementById('destination');
            data.destination.forEach(option => {
                const opt = document.createElement('option');
                opt.textContent = idx+"."+option;
                opt.value = idx++;
                destinationSelect.appendChild(opt);
            });
            destinationSelect.addEventListener("change", function() {
                let mapDocument = document.getElementById("map-frame").contentDocument;
                if (prevDestinationSelect !== null && prevStartSelect !== prevDestinationSelect) {
                    mapDocument.querySelectorAll(".leaflet-marker-pane img")[prevDestinationSelect].src = "https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/images/marker-icon-2x.png";
                }
                mapDocument.querySelectorAll(".leaflet-marker-pane img")[this.value].src = "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png";
                prevDestinationSelect = this.value;
            });

            idx = 0
            const algorithmSelect = document.getElementById('algorithm');
            data.algorithm.forEach(option => {
                const opt = document.createElement('option');
                opt.textContent = option;
                opt.value = idx++;
                algorithmSelect.appendChild(opt);
            });
        });
}
window.onload = populateOptions;

async function getMap(reset) {
    if (reset) {
        window.location.reload();
        return;
    }
    const runButton = document.getElementById('run-button');
    const spinner = document.getElementById('loading-spinner');

    runButton.disabled = true;
    spinner.style.display = "block";

    try {
        const start = document.getElementById('start')?.value;
        const destination = document.getElementById('destination')?.value;
        const algorithm = document.getElementById('algorithm')?.value;
        const apply_sp = document.getElementById('apply_sp').checked ? 1 : 0;

        if (!start || start === "-1" || 
            !destination || destination === "-1" || 
            !algorithm || algorithm === "-1") {
            alert('Please select locations and algorithm.');
            return;
        }

        const mapFrame = document.getElementById('map-frame');
        mapFrame.src = `/get_map?start=${start}&destination=${destination}&algorithm=${algorithm}&apply_sp=${apply_sp}`;

        await new Promise((resolve) => {
            mapFrame.onload = resolve;
        });

        const response = await fetch('/get_data');
        const data = await response.json();

        document.getElementById("max_flow").textContent = "Maximum Flow: " + data.max_flow + " Vehicles/Hour";
        document.getElementById("time").textContent = "Runtime: " + data.runtime + " Seconds";

        const pathContainer = document.getElementById('path-container');
        pathContainer.innerHTML = "";
        const sortedPath = Object.keys(data.color_path).sort((a, b) => a - b);
        sortedPath.forEach(path => {
            const boxContainer = document.createElement('div');
            boxContainer.className = 'path-container';
            boxContainer.style.margin = '0';

            const pathColor = document.createElement('div');
            pathColor.className = 'path-color';
            pathColor.style.backgroundColor = data.color_path[path];
            pathColor.style.width = '20px';
            pathColor.style.height = '20px';
            pathColor.style.borderRadius = '50%';
            pathColor.onclick = () => getMap_static(path);

            const pathName = document.createElement('span');
            pathName.className = 'path-name';
            pathName.style.color = '#333';
            if (path === '-2') {
                pathName.innerText = 'Full path';
            } else if (path === '-1') {
                pathName.innerText = 'Shortest path';
            } else if (path === '0') {
                pathName.innerText = 'Full Push-Relabel';
            } else {
                pathName.innerText = 'Path ' + path;
            }
            pathName.onclick = () => getMap_static(path);

            boxContainer.appendChild(pathColor);
            boxContainer.appendChild(pathName);
            pathContainer.appendChild(boxContainer);
        });
    } catch (error) {
        console.error('Error:', error);
    } finally {
        runButton.disabled = false;
        spinner.style.display = "none";
    }
}

async function getMap_static(map_id) {
    document.getElementById('map-frame').src = `/get_map?map_id=${map_id}`;
}

function filterNames(type) {
    const input = document.getElementById(type+"Search").value.toLowerCase();
    const select = document.getElementById(type);
    const options = select.getElementsByTagName("option");

    for (let option of options) {
        const text = option.textContent.toLowerCase();
        option.style.display = text.includes(input) ? "" : "none";
    }
}