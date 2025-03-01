import React, { useState } from 'react';

const MapControls = ({ onSubmit }) => {
  const [dataset, setDataset] = useState('Ozone');
  const [regionsInput, setRegionsInput] = useState('');
  const [startYear, setStartYear] = useState('2020');
  const [endYear, setEndYear] = useState('2022');

  const handleSubmit = (e) => {
    e.preventDefault();
    const regions = regionsInput
      .split(',')
      .map(r => r.trim())
      .filter(r => r !== '');
    
    onSubmit({
      dataset,
      regions,
      startYear,
      endYear
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="dataset" className="block text-sm font-medium text-gray-700 mb-1">
          Dataset:
        </label>
        <select
          id="dataset"
          value={dataset}
          onChange={(e) => setDataset(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="Ozone">Ozone</option>
          {/* Additional datasets can be added here */}
        </select>
      </div>

      <div>
        <label htmlFor="regionsInput" className="block text-sm font-medium text-gray-700 mb-1">
          Regions (comma separated):
        </label>
        <input
          type="text"
          id="regionsInput"
          value={regionsInput}
          onChange={(e) => setRegionsInput(e.target.value)}
          placeholder="Pune,Ahmadnagar"
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
        />
      </div>

      <div>
        <label htmlFor="startYear" className="block text-sm font-medium text-gray-700 mb-1">
          Start Year:
        </label>
        <input
          type="number"
          id="startYear"
          value={startYear}
          onChange={(e) => setStartYear(e.target.value)}
          placeholder="2020"
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
        />
      </div>

      <div>
        <label htmlFor="endYear" className="block text-sm font-medium text-gray-700 mb-1">
          End Year:
        </label>
        <input
          type="number"
          id="endYear"
          value={endYear}
          onChange={(e) => setEndYear(e.target.value)}
          placeholder="2022"
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
        />
      </div>

      <button
        type="submit"
        className="w-full bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-4 rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
      >
        Generate Maps
      </button>
    </form>
  );
};

export default MapControls;