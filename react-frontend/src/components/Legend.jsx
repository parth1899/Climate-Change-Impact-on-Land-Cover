import React from 'react';

const Legend = ({ legends }) => {
  if (!legends || Object.keys(legends).length === 0) {
    return <div className="legend-container">No legend data available</div>;
  }
  
  return (
    <div className="legend-container">
      {Object.entries(legends).map(([className, color]) => (
        <div className="legend-item" key={className}>
          <div 
            className="legend-color" 
            style={{ backgroundColor: color }}
          />
          <span>{className.charAt(0).toUpperCase() + className.slice(1)} Concentration</span>
        </div>
      ))}
    </div>
  );
};

export default Legend;