// api.js
export class APIHandler {
    constructor(baseUrl = 'http://127.0.0.1:5000') {
      this.baseUrl = baseUrl;
    }
    
    async generateMaps(dataset, startYear, endYear, regions) {
      const url = `${this.baseUrl}/api/generate_maps`;
      const payload = {
        dataset,
        start_year: startYear,
        end_year: endYear,
        selected_regions: regions
      };
      
      try {
        const response = await fetch(url, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        
        return await response.json();
      } catch (error) {
        console.error('Error in generateMaps:', error);
        throw error;
      }
    }
  }
  