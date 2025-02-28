import React from 'react';
import MapContainer from './components/MapContainer';
import './App.css';

function App() {
  return (
    <div className="app">
      <div className="container">
        <h1>NO2 Concentration Maps</h1>
        <MapContainer />
      </div>
    </div>
  );
}

export default App;