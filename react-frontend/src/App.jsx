import React, { useState, useEffect, useRef } from 'react';
import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet';
import { Play, Pause } from 'lucide-react';
import 'leaflet/dist/leaflet.css';
import './index.css';
import { APIHandler } from './services/api';
import MapControls from './components/MapControls';
import RegionSelector from './components/RegionSelector';
import TimeDisplay from './components/TimeDisplay';
import MapLayers from './components/MapLayers';
import StatMarkers from './components/StatMarkers';
import Legend from './components/Legend';

function App() {
  const [urls, setUrls] = useState({});
  const [stats, setStats] = useState({});
  const [legends, setLegends] = useState({});
  const [geojsonData, setGeojsonData] = useState(null);
  const [timePeriods, setTimePeriods] = useState([]);
  const [currentTimeIndex, setCurrentTimeIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [selectedRegions, setSelectedRegions] = useState([]);
  const [availableRegions, setAvailableRegions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const animationRef = useRef(null);
  const apiHandler = useRef(new APIHandler());

  // Extract time periods from URLs
  const getTimePeriods = (urls) => {
    const timeSet = new Set();
    Object.keys(urls).forEach(key => {
      const parts = key.split(' - ');
      if (parts.length === 2) {
        timeSet.add(parts[1]);
      }
    });
    return Array.from(timeSet).sort();
  };

  // Extract regions from URLs
  const getRegions = (urls) => {
    const regionSet = new Set();
    Object.keys(urls).forEach(key => {
      const parts = key.split(' - ');
      if (parts.length === 2) {
        regionSet.add(parts[0]);
      }
    });
    return Array.from(regionSet);
  };

  // Handle form submission
  const handleSubmit = async (formData) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiHandler.current.generateMaps(
        formData.dataset,
        formData.startYear,
        formData.endYear,
        formData.regions
      );

      const { urls, stats, legends, geojson_data } = response;
      setUrls(urls);
      setStats(stats);
      setLegends(legends);
      setGeojsonData(geojson_data);

      const periods = getTimePeriods(urls);
      setTimePeriods(periods);
      setCurrentTimeIndex(0);

      const regions = getRegions(urls);
      setAvailableRegions(regions);
      setSelectedRegions(regions.slice(0, 1)); // Select first region by default
    } catch (error) {
      console.error('Error generating maps:', error);
      setError('Failed to fetch data from the server. Please check if the Flask backend is running.');
    } finally {
      setLoading(false);
    }
  };

  // Toggle play/pause animation
  const togglePlayPause = () => {
    setIsPlaying(prev => !prev);
  };

  // Handle animation
  useEffect(() => {
    if (isPlaying && timePeriods.length > 0) {
      animationRef.current = window.setInterval(() => {
        setCurrentTimeIndex(prevIndex => (prevIndex + 1) % timePeriods.length);
      }, 5000);
    } else if (animationRef.current) {
      clearInterval(animationRef.current);
      animationRef.current = null;
    }

    return () => {
      if (animationRef.current) {
        clearInterval(animationRef.current);
      }
    };
  }, [isPlaying, timePeriods.length]);

  // Get current time period
  const currentTimePeriod = timePeriods[currentTimeIndex] || '';

  // Map center for India
  const center = [20, 77];
  const zoom = 5;

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      <div className="container mx-auto p-4">
        <h1 className="text-2xl font-bold text-center mb-4">Ozone Map Viewer</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="md:col-span-1 bg-white p-4 rounded-lg shadow">
            <MapControls onSubmit={handleSubmit} />
            
            {loading && (
              <div className="mt-4 text-center">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
                <p className="mt-2 text-gray-600">Loading data...</p>
              </div>
            )}
            
            {error && (
              <div className="mt-4 p-3 bg-red-100 text-red-700 rounded-md">
                {error}
              </div>
            )}
            
            {availableRegions.length > 0 && (
              <div className="mt-4">
                <RegionSelector 
                  availableRegions={availableRegions}
                  selectedRegions={selectedRegions}
                  onChange={setSelectedRegions}
                />
              </div>
            )}
            
            {timePeriods.length > 0 && (
              <div className="mt-4 flex items-center">
                <button 
                  onClick={togglePlayPause}
                  className="flex items-center justify-center bg-blue-500 hover:bg-blue-600 text-white px-3 py-2 rounded"
                >
                  {isPlaying ? <Pause size={16} /> : <Play size={16} />}
                  <span className="ml-2">{isPlaying ? 'Pause' : 'Play'}</span>
                </button>
                <TimeDisplay timePeriod={currentTimePeriod} />
              </div>
            )}
          </div>
          
          <div className="md:col-span-3 bg-white p-4 rounded-lg shadow">
            <div className="h-[600px] w-full relative">
              <MapContainer 
                center={center} 
                zoom={zoom} 
                style={{ height: '100%', width: '100%' }}
              >
                <TileLayer
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                
                {geojsonData && (
                  <GeoJSON 
                    data={geojsonData}
                    style={{
                      color: '#3388ff',
                      weight: 2,
                      opacity: 1,
                      fillOpacity: 0.1
                    }}
                  />
                )}
                
                <MapLayers 
                  urls={urls}
                  selectedRegions={selectedRegions}
                  currentTimePeriod={currentTimePeriod}
                />
                
                <StatMarkers 
                  stats={stats}
                  selectedRegions={selectedRegions}
                  currentTimePeriod={currentTimePeriod}
                  geojsonData={geojsonData}
                />
                
                <Legend legends={legends} />
              </MapContainer>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;