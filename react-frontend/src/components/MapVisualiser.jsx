import React, { useEffect, useRef } from "react";
import L from "leaflet";

const MapVisualiser = ({ mapData }) => {
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);

  useEffect(() => {
    if (!mapInstanceRef.current) {
      mapInstanceRef.current = L.map(mapRef.current).setView(
        [19.076, 72.8777],
        6
      );

      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "© OpenStreetMap contributors",
      }).addTo(mapInstanceRef.current);
    }

    if (mapData) {
      mapInstanceRef.current.eachLayer((layer) => {
        if (layer instanceof L.TileLayer === false) {
          mapInstanceRef.current.removeLayer(layer);
        }
      });

      if (mapData.map_urls) {
        Object.values(mapData.map_urls).forEach((url) => {
          L.tileLayer(url, {
            attribution: "NO2 Concentration Map",
          }).addTo(mapInstanceRef.current);
        });
      }
    }

    return () => {
    };
  }, [mapData]);

  return <div ref={mapRef} className="map" />;
};

export default MapVisualiser;
