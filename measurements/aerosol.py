import ee
import pandas as pd
import uuid
from typing import List, Dict, Any
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from config import initialize_earth_engine

class AERAIDataProcessor:
    def __init__(self, params: Dict[str, Any]):
        """
        Initialize AERAIDataProcessor with parameters.
        
        Args:
            params (Dict[str, Any]): Dictionary containing:
                - start_date (str): Start date in ISO format (e.g., 'YYYY-MM-DDTHH:MM:SSZ')
                - end_date (str): End date in ISO format (e.g., 'YYYY-MM-DDTHH:MM:SSZ')
                - geojson_path (str): Path to GeoJSON file with district boundaries
        """
        # Initialize Earth Engine
        initialize_earth_engine()
        
        self.params = params
        self.CONFIG = {
            'AER_AI_COLLECTION': 'COPERNICUS/S5P/NRTI/L3_AER_AI',
            'SCALE': 1113,  # meters; using pixel size ~1113.2 meters for AER AI data
            'MAX_PIXELS': 1e13,
            'TILE_SCALE': 4,
        }
        
        self.GEOJSON_PATH = params.get('geojson_path', '../boundaries/datasets/maharashtra_districts.geojson')
        
        # Define bands to extract for the AER AI dataset
        self.BANDS = [
            'absorbing_aerosol_index',
            'sensor_altitude',
            'sensor_azimuth_angle',
            'sensor_zenith_angle',
            'solar_azimuth_angle',
            'solar_zenith_angle'
        ]
    
    def _load_districts(self) -> List[Dict]:
        """Load all districts from the GeoJSON file."""
        try:
            with open(self.GEOJSON_PATH, 'r') as f:
                geojson_data = json.load(f)
            
            districts = []
            for feature in geojson_data['features']:
                district_name = feature['properties'].get('shapeName', 
                                feature['properties'].get('shapeName_1', 'Unknown'))
                
                coords = feature['geometry']['coordinates']
                geom_type = feature['geometry']['type']
                
                if geom_type == 'MultiPolygon':
                    geometry = ee.Geometry.MultiPolygon(coords)
                elif geom_type == 'Polygon':
                    geometry = ee.Geometry.Polygon(coords)
                else:
                    print(f"Unsupported geometry type for {district_name}: {geom_type}")
                    continue
                
                districts.append({
                    'name': district_name,
                    'geometry': geometry
                })
            
            return districts
        except Exception as e:
            raise ValueError(f"Error loading districts: {str(e)}")
    
    def _get_aer_ai_data_for_interval(self, district: Dict, interval_start: str, interval_end: str) -> Dict:
        """
        Get a composite AER AI measurement for a district over a given time interval.
        
        Args:
            district (Dict): A dictionary with 'name' and 'geometry' for the district.
            interval_start (str): Start date (ISO format) for the interval.
            interval_end (str): End date (ISO format) for the interval.
            
        Returns:
            Dict: A dictionary with measurement details.
        """
        try:
            ee_start = ee.Date(interval_start)
            ee_end = ee.Date(interval_end)
            
            # Filter the collection to the interval and select the specified bands
            collection = ee.ImageCollection(self.CONFIG['AER_AI_COLLECTION']) \
                .filterDate(ee_start, ee_end) \
                .select(self.BANDS)
            
            # Create a composite image (mean over the interval)
            image = collection.mean()
            
            # Create a timestamp string representing the interval
            timestamp = f"{interval_start} to {interval_end}"
            measurement_id = str(uuid.uuid4())
            
            # Extract mean values over the district geometry
            stats = image.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=district['geometry'],
                scale=self.CONFIG['SCALE'],
                maxPixels=self.CONFIG['MAX_PIXELS'],
                tileScale=self.CONFIG['TILE_SCALE']
            ).getInfo()
            
            result = {
                'district_name': district['name'],
                'measurement_id': measurement_id,
                'timestamp': timestamp,
                'dataset': 'Sentinel-5P NRTI AER AI'
            }
            
            # Add each band value to the result
            for band in self.BANDS:
                result[band] = stats.get(band, None)
                
            return result
        except Exception as e:
            print(f"Error getting AER AI data for {district['name']} in interval {interval_start} - {interval_end}: {str(e)}")
            return {}
    
    def process_data(self) -> pd.DataFrame:
        """Process AER AI data for all districts over weekly intervals and return a DataFrame."""
        try:
            start_date_str = self.params.get('start_date', '2018-07-10T11:02:44Z')
            end_date_str = self.params.get('end_date', '2025-02-25T08:56:13Z')
            
            # Remove the trailing 'Z' and convert to datetime objects
            start_date = datetime.strptime(start_date_str.rstrip('Z'), '%Y-%m-%dT%H:%M:%S')
            end_date = datetime.strptime(end_date_str.rstrip('Z'), '%Y-%m-%dT%H:%M:%S')
            
            print(f"Start date: {start_date}")
            print(f"End date: {end_date}")
            
            # Generate weekly intervals between start and end dates
            intervals = []
            current = start_date
            while current < end_date:
                next_interval = current + timedelta(days=7)
                interval_end = min(next_interval, end_date)
                intervals.append((current.strftime('%Y-%m-%dT%H:%M:%S'), interval_end.strftime('%Y-%m-%dT%H:%M:%S')))
                current = next_interval
            
            # Print generated intervals (for debugging purposes)
            for start, end in intervals:
                print(f"Interval: {start} to {end}")
            
            # Load district geometries from GeoJSON
            districts = self._load_districts()
            print(f"Loaded {len(districts)} districts")
            
            all_data = []
            print(f"Processing data for {len(districts)} districts over {len(intervals)} intervals")
            with ThreadPoolExecutor() as executor:
                futures = []
                # Submit a task for each district and each time interval
                for district in districts:
                    for (interval_start, interval_end) in intervals:
                        future = executor.submit(
                            self._get_aer_ai_data_for_interval, district, interval_start, interval_end
                        )
                        futures.append(future)
                
                # Collect results from all futures
                for future in futures:
                    result = future.result()
                    if result:  # Only add if result is not empty
                        all_data.append(result)
            
            return pd.DataFrame(all_data)
        except Exception as e:
            print(f"Error in process_data: {str(e)}")
            return pd.DataFrame()
    
    def export_to_csv(self, filename: str = 'datasets/aer_ai_measurements.csv'):
        """Process data and export the results to a CSV file."""
        df = self.process_data()
        if not df.empty:
            df.to_csv(filename, index=False)
            print(f"Exported {len(df)} measurements to {filename}")
        else:
            print("No data to export")

# Example usage:
if __name__ == "__main__":
    params = {
        'start_date': '2018-07-10T11:17:44Z',
        'end_date': '2025-02-26T10:16:13Z',  # Adjust the dates as needed
        'geojson_path': '../boundaries/datasets/maharashtra_districts.geojson'
    }
    
    processor = AERAIDataProcessor(params)
    processor.export_to_csv()
