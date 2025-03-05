// main.js
import { APIHandler } from './JS/api.js';
import { MapHandler } from './JS/map.js';

document.addEventListener('DOMContentLoaded', () => {
  const apiHandler = new APIHandler();  // Adjust base URL if needed.
  const mapHandler = new MapHandler();
  
  const form = document.getElementById('mapForm');
  const playPauseBtn = document.getElementById('playPauseBtn');
  
  // Animation variables.
  let timePeriods = [];
  let currentIndex = 0;
  let animationInterval = null;
  let isPlaying = false;
  let urlsGlobal = {}; // Store URLs from the API response.
  let statsGlobal = {}; // Store numerical stats from the API response.
  
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    
    // Retrieve user inputs.
    const dataset = document.getElementById('dataset').value;
    const regionsInput = document.getElementById('regionsInput').value;
    const regions = regionsInput.split(',').map(r => r.trim()).filter(r => r !== '');
    const startYear = document.getElementById('startYear').value;
    const endYear = document.getElementById('endYear').value;
    
    try {
      // Call backend endpoint.
      const response = await apiHandler.generateMaps(dataset, startYear, endYear, regions);
      // Destructure stats along with urls, legends, and geojson_data.
      const { urls, stats, legends, geojson_data } = response;
      urlsGlobal = urls;
      statsGlobal = stats;
      
      // Load geoJSON boundaries and update legend.
      mapHandler.loadGeoJSON(geojson_data);
      mapHandler.updateLegend(legends);
      // Populate the multi-select region dropdown.
      mapHandler.populateRegionSelector(urls);
      
      // Get time periods (e.g., "2020-01", "2020-02", …) and initialize index.
      timePeriods = mapHandler.getTimePeriods(urls);
      currentIndex = 0;
      
      // Clear any existing overlays and display the first time period.
      if (timePeriods.length > 0) {
        mapHandler.clearOverlays();
        mapHandler.updateMapLayers(urls, timePeriods[currentIndex]);
        // Also update stat markers.
        mapHandler.updateStatMarkers(stats, timePeriods[currentIndex]);
      }
      
    } catch (error) {
      console.error('Error generating maps:', error);
    }
  });
  
  // Update overlays and stat markers if region selections change.
  mapHandler.regionSelector.addEventListener('change', () => {
    if (timePeriods.length > 0) {
      mapHandler.updateMapLayers(urlsGlobal, timePeriods[currentIndex]);
      mapHandler.updateStatMarkers(statsGlobal, timePeriods[currentIndex]);
    }
  });
  
  // Play/Pause button toggles time animation.
  playPauseBtn.addEventListener('click', () => {
    if (!isPlaying) {
      // Start animation.
      isPlaying = true;
      playPauseBtn.textContent = 'Pause';
      animationInterval = setInterval(() => {
        currentIndex = (currentIndex + 1) % timePeriods.length;
        mapHandler.updateMapLayers(urlsGlobal, timePeriods[currentIndex]);
        mapHandler.updateStatMarkers(statsGlobal, timePeriods[currentIndex]);
      }, 5000); // 5-second delay between layers.
    } else {
      // Pause animation.
      isPlaying = false;
      playPauseBtn.textContent = 'Play';
      clearInterval(animationInterval);
    }
  });
});
