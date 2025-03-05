import ee
import pandas as pd
import uuid
from typing import List, Dict, Any
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta  # for generating monthly intervals
from config import initialize_earth_engine

class CODataProcessor:
    def __init__(self, params: Dict[str, Any]):
        """
        Initialize CODataProcessor with parameters.
        
        Args:
            params (Dict[str, Any]): Dictionary containing:
                - start_date (str): Start date in YYYY-MM-DD format
                - end_date (str): End date in YYYY-MM-DD format
                - geojson_path (str): Path to GeoJSON file with district boundaries
        """
        # Initialize Earth Engine
        initialize_earth_engine()
        
        self.params = params
        self.CONFIG = {
            'CO_COLLECTION': 'COPERNICUS/S5P/NRTI/L3_CO',
            'SCALE': 1000,  # meters
            'MAX_PIXELS': 1e13,
            'TILE_SCALE': 4,
        }
        
        self.GEOJSON_PATH = params.get('geojson_path', '../boundaries/datasets/maharashtra_districts.geojson')
        
        # Define bands to extract
        self.BANDS = [
            'CO_column_number_density',
            'H2O_column_number_density',
            'cloud_height',
            'sensor_altitude',
            'sensor_azimuth_angle',
            'sensor_zenith_angle',
            'solar_azimuth_angle',
            'solar_zenith_angle'
        ]
    
    def _load_districts(self) -> List[Dict]:
        """Load all districts from GeoJSON file"""
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
    
    def _get_co_data_for_interval(self, district: Dict, interval_start: str, interval_end: str) -> Dict:
        """
        Get a composite CO measurement for a district over a given time interval.
        
        Args:
            district (Dict): A dictionary with 'name' and 'geometry' for the district.
            interval_start (str): Start date (YYYY-MM-DD) for the interval.
            interval_end (str): End date (YYYY-MM-DD) for the interval.
            
        Returns:
            Dict: A dictionary with measurement details.
        """
        try:
            ee_start = ee.Date(interval_start)
            ee_end = ee.Date(interval_end)
            
            # Filter collection to the interval and select bands
            collection = ee.ImageCollection(self.CONFIG['CO_COLLECTION']) \
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
                'dataset': 'Sentinel-5P NRTI CO'
            }
            
            # Add each band value to the result
            for band in self.BANDS:
                result[band] = stats.get(band, None)
                
            return result
        except Exception as e:
            print(f"Error getting CO data for {district['name']} in interval {interval_start} - {interval_end}: {str(e)}")
            return {}
    
    def process_data(self) -> pd.DataFrame:
        """Process CO data for all districts over monthly intervals and return a DataFrame."""
        try:
            # start_date_str = self.params.get('start_date', '2020-01-01')
            # end_date_str = self.params.get('end_date', '2020-12-31')
            
            # Generate monthly intervals between start and end dates
            # start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            # end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            # intervals = []
            # current = start_date
            # while current < end_date:
            #     next_interval = current + relativedelta(months=1)
            #     # Ensure the interval end does not go past the overall end_date
            #     interval_end = min(next_interval, end_date)
            #     intervals.append((current.strftime('%Y-%m-%d'), interval_end.strftime('%Y-%m-%d')))
            #     current = next_interval
            
            # Generate two-day intervals between start and end dates
            # start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            # end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            # intervals = []
            # current = start_date
            # while current < end_date:
            #     next_interval = current + timedelta(days=2)
            #     # Ensure the interval end does not go past the overall end_date
            #     interval_end = min(next_interval, end_date)
            #     intervals.append((current.strftime('%Y-%m-%d'), interval_end.strftime('%Y-%m-%d')))
            #     current = next_interval

            # Provided date range strings
            start_date_str = '2018-11-22T12:00:13Z'
            end_date_str = '2025-02-25T08:56:13Z'

            # Remove the trailing 'Z' and convert to datetime objects
            start_date = datetime.strptime(start_date_str.rstrip('Z'), '%Y-%m-%dT%H:%M:%S')
            end_date = datetime.strptime(end_date_str.rstrip('Z'), '%Y-%m-%dT%H:%M:%S')

            print(f"Start date: {start_date}")
            print(f"End date: {end_date}")

            # Generate weekly intervals
            intervals = []
            current = start_date
            while current < end_date:
                next_interval = current + timedelta(days=7)
                # Ensure we don't exceed the overall end_date
                interval_end = min(next_interval, end_date)
                intervals.append((current.strftime('%Y-%m-%dT%H:%M:%S'), interval_end.strftime('%Y-%m-%dT%H:%M:%S')))
                current = next_interval

            # Example: print the generated intervals
            for start, end in intervals:
                print(f"Interval: {start} to {end}")

            # Load all districts from GeoJSON
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
                            self._get_co_data_for_interval, district, interval_start, interval_end
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
    
    def export_to_csv(self, filename: str = 'datasets/co_measurements.csv'):
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
        'start_date': '2020-01-01',
        'end_date': '2021-01-01',  # Example: one month of data
        'geojson_path': '../boundaries/datasets/maharashtra_districts.geojson'
    }
    
    processor = CODataProcessor(params)
    processor.export_to_csv()
