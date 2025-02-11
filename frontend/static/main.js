// main.js
document.addEventListener('DOMContentLoaded', () => {
    const showMapBtn = document.getElementById('show-map-btn');
    const mapVisualizer = new MapVisualizer('map', 'legend-container');

    showMapBtn.addEventListener('click', async () => {
        // Collect input values
        const region = document.getElementById('region').value.trim();
        
        // Collect selected years
        const selectedYears = Array.from(
            document.querySelectorAll('input[name="years"]:checked')
        ).map(checkbox => parseInt(checkbox.value));
        
        // Collect selected classes
        const selectedClasses = Array.from(
            document.querySelectorAll('input[name="classes"]:checked')
        ).map(checkbox => checkbox.value);

        // Validation
        if (!region) {
            alert('Please enter a region name');
            return;
        }
        if (selectedYears.length === 0) {
            alert('Please select at least one year');
            return;
        }
        if (selectedClasses.length === 0) {
            alert('Please select at least one concentration class');
            return;
        }

        try {
            // Clear previous map layers and legend
            mapVisualizer.clearPreviousLayers();

            // Fetch map data
            const mapData = await fetchMapData(region, selectedYears, selectedClasses);

            // Add tile layers for each map URL
            Object.values(mapData.map_urls).forEach(url => {
                mapVisualizer.addTileLayer(url);
            });

            // Create legend
            mapVisualizer.createLegend(mapData.legends);

        } catch (error) {
            alert('Failed to fetch map data. Please try again.');
            console.error(error);
        }
    });
});