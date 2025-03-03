import React, { useEffect, useState } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';

const StatMarkers = ({
  stats,
  selectedRegions,
  currentTimePeriod,
  geojsonData
}) => {
  const map = useMap();
  const [markers, setMarkers] = useState({});

  useEffect(() => {
    if (!geojsonData || !geojsonData.features) return;

    // Remove markers for regions that are no longer selected
    Object.keys(markers).forEach(region => {
      if (!selectedRegions.includes(region)) {
        map.removeLayer(markers[region]);
      }
    });

    // Create new markers object
    const newMarkers = {};

    // Add or update markers for selected regions
    selectedRegions.forEach(region => {
      // Find the corresponding GeoJSON feature
      const feature = geojsonData.features.find(
        (f) => f.properties.shapeName === region
      );

      if (feature) {
        // Compute the centroid of the feature
        const bounds = L.geoJSON(feature).getBounds();
        const center = bounds.getCenter();

        // Build the key as used in the stats dictionary
        const key = `${region} - ${currentTimePeriod}`;
        let statValue = stats[key];
        statValue = statValue !== undefined ? parseFloat(statValue).toFixed(4) : 'N/A';

        // If a marker already exists for this region, update it
        if (markers[region]) {
          markers[region].setLatLng(center);
          markers[region].setTooltipContent(
            `<strong>${region}</strong><br>O3: ${statValue}`
          );
          newMarkers[region] = markers[region];
        } else {
          // Create a new marker and bind a tooltip that is permanently visible
          const marker = L.marker(center).bindTooltip(
            `<strong>${region}</strong><br>O3: ${statValue}`,
            {
              direction: 'top',
              permanent: true,
              className: 'stat-tooltip'
            }
          );
          marker.addTo(map);
          newMarkers[region] = marker;
        }
      }
    });

    setMarkers(newMarkers);

    // Cleanup function to remove all markers when component unmounts
    return () => {
      Object.values(newMarkers).forEach(marker => {
        map.removeLayer(marker);
      });
    };
  }, [map, stats, selectedRegions, currentTimePeriod, geojsonData]);

  return null;
};

export default StatMarkers;