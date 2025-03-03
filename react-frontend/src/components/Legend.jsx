import React, { useEffect } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';

const Legend = ({ legends }) => {
  const map = useMap();

  useEffect(() => {
    // Create legend control if it doesn't exist
    const legendControl = L.control({ position: 'bottomright' });

    legendControl.onAdd = () => {
      const div = L.DomUtil.create('div', 'info legend');
      let legendHtml = '<h4 class="font-bold mb-2">Legend</h4>';
      
      for (const key in legends) {
        legendHtml += `
          <div class="flex items-center mb-1">
            <span style="background: ${legends[key]}; width: 18px; height: 18px; display: inline-block; margin-right: 8px;"></span>
            <span>${key}</span>
          </div>
        `;
      }
      
      div.innerHTML = legendHtml;
      div.style.padding = '6px 8px';
      div.style.background = 'white';
      div.style.background = 'rgba(255, 255, 255, 0.8)';
      div.style.boxShadow = '0 0 15px rgba(0, 0, 0, 0.2)';
      div.style.borderRadius = '5px';
      div.style.lineHeight = '1.5';
      div.style.color = '#555';
      
      return div;
    };

    legendControl.addTo(map);

    // Cleanup function to remove legend when component unmounts
    return () => {
      legendControl.remove();
    };
  }, [map, legends]);

  return null;
};

export default Legend;