// map.js
class MapVisualizer {
    constructor(mapElementId, legendContainerId) {
        this.map = L.map(mapElementId).setView([19.0760, 72.8777], 6);
        this.legendContainer = document.getElementById(legendContainerId);
        
        // Add OpenStreetMap base layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(this.map);
    }

    clearPreviousLayers() {
        // Remove all existing layers except the base layer
        this.map.eachLayer((layer) => {
            if (layer instanceof L.TileLayer === false) {
                this.map.removeLayer(layer);
            }
        });
        
        // Clear previous legend
        this.legendContainer.innerHTML = '';
    }

    addTileLayer(url, className) {
        const tileLayer = L.tileLayer(url, {
            attribution: 'NO2 Concentration Map'
        }).addTo(this.map);
    }

    createLegend(legends) {
        for (const [className, color] of Object.entries(legends)) {
            const legendItem = document.createElement('div');
            legendItem.classList.add('legend-item');
            
            const colorBox = document.createElement('div');
            colorBox.classList.add('legend-color');
            colorBox.style.backgroundColor = color;
            
            const label = document.createElement('span');
            label.textContent = `${className.charAt(0).toUpperCase() + className.slice(1)} Concentration`;
            
            legendItem.appendChild(colorBox);
            legendItem.appendChild(label);
            
            this.legendContainer.appendChild(legendItem);
        }
    }
}