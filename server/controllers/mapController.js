const mapData = {

    maharashtra: {
      2019: {
        low: 'https://example.com/tiles/maharashtra/2019/low/{z}/{x}/{y}.png',
        medium: 'https://example.com/tiles/maharashtra/2019/medium/{z}/{x}/{y}.png',
        high: 'https://example.com/tiles/maharashtra/2019/high/{z}/{x}/{y}.png'
      },
      2020: {
        low: 'https://example.com/tiles/maharashtra/2020/low/{z}/{x}/{y}.png',
        medium: 'https://example.com/tiles/maharashtra/2020/medium/{z}/{x}/{y}.png',
        high: 'https://example.com/tiles/maharashtra/2020/high/{z}/{x}/{y}.png'
      }
    },

    delhi: {
      2019: {
        low: 'https://example.com/tiles/delhi/2019/low/{z}/{x}/{y}.png',
        medium: 'https://example.com/tiles/delhi/2019/medium/{z}/{x}/{y}.png',
        high: 'https://example.com/tiles/delhi/2019/high/{z}/{x}/{y}.png'
      },
      2020: {
        low: 'https://example.com/tiles/delhi/2020/low/{z}/{x}/{y}.png',
        medium: 'https://example.com/tiles/delhi/2020/medium/{z}/{x}/{y}.png',
        high: 'https://example.com/tiles/delhi/2020/high/{z}/{x}/{y}.png'
      }
    }
  };
  
  const legendColors = {
    low: '#ADD8E6',    
    medium: '#4682B4', 
    high: '#00008B'    
  };
  
  exports.generateMaps = async (req, res) => {
    try {
      const { region_name, selected_years, selected_classes } = req.body;
  
      if (!region_name || !selected_years || !selected_classes) {
        return res.status(400).json({ 
          success: false, 
          error: 'Missing required parameters' 
        });
      }
      
      if (selected_years.length === 0 || selected_classes.length === 0) {
        return res.status(400).json({ 
          success: false, 
          error: 'At least one year and one class must be selected' 
        });
      }
  
      const regionKey = region_name.toLowerCase();
      
      if (!mapData[regionKey]) {
        return res.status(404).json({
          success: false,
          error: `No data available for region: ${region_name}`
        });
      }
  
      const map_urls = {};
      const legends = {};
  
      selected_years.forEach(year => {
        if (mapData[regionKey][year]) {
          selected_classes.forEach(classType => {
            if (mapData[regionKey][year][classType]) {
              const mapKey = `${year}_${classType}`;
              map_urls[mapKey] = mapData[regionKey][year][classType];
              legends[classType] = legendColors[classType];
            }
          });
        }
      });
  
      if (Object.keys(map_urls).length === 0) {
        return res.status(404).json({
          success: false,
          error: 'No map data found for the selected criteria'
        });
      }
  
      res.json({
        success: true,
        map_urls,
        legends,
        region: region_name
      });
      
    } catch (error) {
      console.error('Error generating maps:', error);
      res.status(500).json({ 
        success: false, 
        error: 'Server error' 
      });
    }
  };