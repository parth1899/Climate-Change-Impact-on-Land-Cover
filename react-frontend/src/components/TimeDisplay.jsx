import React from 'react';

const TimeDisplay = ({ timePeriod }) => {
  return (
    <span className="ml-3 font-bold text-gray-700">
      {timePeriod || 'No time period selected'}
    </span>
  );
};

export default TimeDisplay;