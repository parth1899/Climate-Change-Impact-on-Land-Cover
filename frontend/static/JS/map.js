// map.js
export class MapHandler {
    constructor() {
      // Initialize Leaflet map centered over India.
      this.map = L.map('map').setView([20, 77], 5);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
      }).addTo(this.map);
      
      // Object to hold overlay layers for each region.
      this.overlays = {};
      
      // Legend control.
      this.legendControl = L.control({ position: 'bottomright' });
      this.legendControl.onAdd = (map) => {
        const div = L.DomUtil.create('div', 'info legend');
        div.innerHTML = '<h4>Legend</h4>';
        return div;
      };
      this.legendControl.addTo(this.map);
      
      // Multi-select region element.
      this.regionSelector = document.getElementById('regionSelector');
      // Time display element to show current month/year.
      this.timeDisplay = document.getElementById('timeDisplay');
      
      // Object to hold stat markers keyed by region.
      this.statMarkers = {};
      
      // Store loaded geojson data for marker lookup.
      this.geojsonData = null;
    }
    
    updateLegend(legends) {
      const div = this.legendControl.getContainer();
      let legendHtml = '<h4>Legend</h4>';
      for (const key in legends) {
        legendHtml += `<i style="background: ${legends[key]}; width: 18px; height: 18px; display: inline-block; margin-right: 8px;"></i>${key}<br>`;
      }
      div.innerHTML = legendHtml;
    }
    
    loadGeoJSON(geojson) {
      if (this.geojsonLayer) {
        this.map.removeLayer(this.geojsonLayer);
      }
      this.geojsonLayer = L.geoJSON(geojson, {
        style: {
          color: '#3388ff',
          weight: 2,
          opacity: 1,
          fillOpacity: 0.1
        }
      }).addTo(this.map);
      this.map.fitBounds(this.geojsonLayer.getBounds());
      // Store geojson data for marker creation.
      this.geojsonData = geojson;
    }
    
    // Populate the multi-select region list based on the keys from the returned URLs.
    populateRegionSelector(urls) {
      this.regionSelector.innerHTML = '';
      const regionSet = new Set();
      Object.keys(urls).forEach(key => {
        // Expected key format: "RegionName - YYYY-MM"
        const parts = key.split(' - ');
        if (parts.length === 2) {
          regionSet.add(parts[0]);
        }
      });
      regionSet.forEach(region => {
        const option = document.createElement('option');
        option.value = region;
        option.textContent = region;
        this.regionSelector.appendChild(option);
      });
    }
    
    // Extract a sorted list of unique time periods from the URLs.
    getTimePeriods(urls) {
      const timeSet = new Set();
      Object.keys(urls).forEach(key => {
        const parts = key.split(' - ');
        if (parts.length === 2) {
          timeSet.add(parts[1]);
        }
      });
      return Array.from(timeSet).sort();
    }
    
    // Remove any existing overlay layers.
    clearOverlays() {
      for (const region in this.overlays) {
        this.map.removeLayer(this.overlays[region]);
      }
      this.overlays = {};
    }
    
    // Update overlays for all currently selected regions given the current time period.
    updateMapLayers(urls, currentTime) {
      // Update the time display.
      this.timeDisplay.textContent = currentTime;
      
      // Get all selected regions.
      const selectedRegions = Array.from(this.regionSelector.selectedOptions).map(opt => opt.value);
      selectedRegions.forEach(region => {
        const key = `${region} - ${currentTime}`;
        const url = urls[key];
        if (url) {
          // Remove existing overlay for the region if it exists.
          if (this.overlays[region]) {
            this.map.removeLayer(this.overlays[region]);
          }
          // Create and add a new tile layer for the region.
          const layer = L.tileLayer(url, { opacity: 0.7 });
          layer.addTo(this.map);
          this.overlays[region] = layer;
        } else {
          console.warn('No URL found for key:', key);
        }
      });
      
      // Remove overlays for any regions that are no longer selected.
      for (const region in this.overlays) {
        if (!selectedRegions.includes(region)) {
          this.map.removeLayer(this.overlays[region]);
          delete this.overlays[region];
        }
      }
    }
    
    // Update statistical markers (pins) for the selected regions using the stats data.
    // This method updates existing markers or creates new ones so they always remain visible.
    updateStatMarkers(stats, currentTime) {
        // Get selected regions.
        const selectedRegions = Array.from(this.regionSelector.selectedOptions).map(opt => opt.value);
      
        selectedRegions.forEach(region => {
          // Find the corresponding GeoJSON feature.
          let feature = null;
          if (this.geojsonData && this.geojsonData.features) {
            feature = this.geojsonData.features.find(f => f.properties.shapeName === region);
          }
          
          if (feature) {
            // Compute the centroid of the feature.
            const bounds = L.geoJSON(feature).getBounds();
            const center = bounds.getCenter();
            // Build the key as used in the stats dictionary.
            const key = `${region} - ${currentTime}`;
            let statValue = stats[key];
            statValue = (statValue !== null && statValue !== undefined) ? parseFloat(statValue).toFixed(4) : "N/A";
            
            // If a marker already exists for this region, update it.
            if (this.statMarkers[region]) {
              this.statMarkers[region].setLatLng(center);
              this.statMarkers[region].setTooltipContent(`<strong>${region}</strong><br>O3: ${statValue}`);
            } else {
              // Create a new marker and bind a tooltip that is permanently visible.
              const marker = L.marker(center).bindTooltip(
                `<strong>${region}</strong><br>O3: ${statValue}`, 
                { direction: 'top', permanent: true, className: 'stat-tooltip' }
              );
              marker.addTo(this.map);
              this.statMarkers[region] = marker;
            }
          }
        });
        
        // Remove markers for any regions that are no longer selected.
        for (const region in this.statMarkers) {
          if (!selectedRegions.includes(region)) {
            this.map.removeLayer(this.statMarkers[region]);
            delete this.statMarkers[region];
          }
        }
      }      
  }
  