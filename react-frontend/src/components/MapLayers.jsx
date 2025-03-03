import React, { useEffect, useState } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';

const MapLayers = ({
  urls,
  selectedRegions,
  currentTimePeriod
}) => {
  const map = useMap();
  const [layers, setLayers] = useState({});

  useEffect(() => {
    // Remove any layers that are no longer selected
    Object.keys(layers).forEach(region => {
      if (!selectedRegions.includes(region)) {
        map.removeLayer(layers[region]);
      }
    });

    // Create new layers object
    const newLayers = {};

    // Add or update layers for selected regions
    selectedRegions.forEach(region => {
      const key = `${region} - ${currentTimePeriod}`;
      const url = urls[key];

      if (url) {
        // Remove existing layer if it exists
        if (layers[region]) {
          map.removeLayer(layers[region]);
        }

        // Create and add new layer
        const layer = L.tileLayer(url, { opacity: 0.7 });
        layer.addTo(map);
        newLayers[region] = layer;
      }
    });

    setLayers(newLayers);

    // Cleanup function to remove all layers when component unmounts
    return () => {
      Object.values(newLayers).forEach(layer => {
        map.removeLayer(layer);
      });
    };
  }, [map, urls, selectedRegions, currentTimePeriod]);

  return null;
};

export default MapLayers;