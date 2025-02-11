// api.js
const API_BASE_URL = 'http://localhost:5000';

async function fetchMapData(region, years, classes) {
    try {
        const response = await fetch(`${API_BASE_URL}/generate_maps`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                region_name: region,
                selected_years: years,
                selected_classes: classes
            })
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        return await response.json();
    } catch (error) {
        console.error('Error fetching map data:', error);
        throw error;
    }
}