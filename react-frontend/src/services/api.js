import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || '/api';

export const fetchMapData = async (region, years, classes) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/maps/generate`, {
      region_name: region,
      selected_years: years,
      selected_classes: classes
    });

    return response.data;
  } catch (error) {
    console.error('Error fetching map data:', error);
    throw error;
  }
};