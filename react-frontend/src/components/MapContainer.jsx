import React, { useState } from "react";
import InputForm from "./InputForm";
import MapVisualiser from "./MapVisualiser";
import Legend from "./Legend";
import { fetchMapData } from "../services/api";

const MapContainer = () => {
  const [mapData, setMapData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFormSubmit = async (formData) => {
    try {
      setLoading(true);
      setError(null);

      const data = await fetchMapData(
        formData.region,
        formData.years,
        formData.classes
      );

      setMapData(data);
    } catch (err) {
      setError("Failed to fetch map data. Please try again.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="map-section">
      <InputForm onSubmit={handleFormSubmit} />

      {loading && <div className="loading">Loading map data...</div>}
      {error && <div className="error">{error}</div>}

      <div className="map-container">
        <MapVisualiser mapData={mapData} />
        {mapData && <Legend legends={mapData.legends} />}
      </div>
    </div>
  );
};

export default MapContainer;
