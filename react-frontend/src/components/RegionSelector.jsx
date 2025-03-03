import React from 'react';

const RegionSelector = ({
  availableRegions,
  selectedRegions,
  onChange
}) => {
  const handleChange = (e) => {
    const options = Array.from(e.target.selectedOptions);
    const values = options.map(option => option.value);
    onChange(values);
  };

  return (
    <div>
      <label htmlFor="regionSelector" className="block text-sm font-medium text-gray-700 mb-1">
        Select Regions (Ctrl+Click for multiple):
      </label>
      <select
        id="regionSelector"
        multiple
        value={selectedRegions}
        onChange={handleChange}
        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 h-32"
      >
        {availableRegions.map(region => (
          <option key={region} value={region}>
            {region}
          </option>
        ))}
      </select>
    </div>
  );
};

export default RegionSelector;