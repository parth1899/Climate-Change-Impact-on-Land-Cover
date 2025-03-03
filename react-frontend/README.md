# Ozone Map Viewer

A React application for visualizing ozone data on maps. This application works with a Flask backend to fetch and display ozone data for different regions and time periods.

## Features

- Interactive map visualization of ozone data
- Region selection for comparing different areas
- Time-based animation to see changes over time
- Statistical data display for selected regions
- Responsive design that works on desktop and mobile devices

## Setup Instructions

### Frontend (React)

1. Install dependencies:
   ```
   npm install
   ```

2. Start the development server:
   ```
   npm run dev
   ```

### Backend (Flask)

The frontend is designed to work with a Flask backend that should:

1. Provide an API endpoint at `/api/generate_maps`
2. Accept POST requests with the following JSON structure:
   ```json
   {
     "dataset": "Ozone",
     "start_year": "2020",
     "end_year": "2022",
     "selected_regions": ["Pune", "Ahmadnagar"]
   }
   ```
3. Return data in the following format:
   ```json
   {
     "urls": {
       "Region - TimeStamp": "tile_url",
       ...
     },
     "stats": {
       "Region - TimeStamp": "value",
       ...
     },
     "legends": {
       "Low": "#00ff00",
       "Medium": "#ffff00",
       "High": "#ff0000"
     },
     "geojson_data": {
       "type": "FeatureCollection",
       "features": [...]
     }
   }
   ```

## Technologies Used

- React
- Leaflet (via react-leaflet)
- Tailwind CSS
- Vite