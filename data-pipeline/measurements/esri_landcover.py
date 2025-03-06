import ee
import pandas as pd
import uuid
from typing import List, Dict, Any
import json
from concurrent.futures import ThreadPoolExecutor
from config import initialize_earth_engine

# Initialize Earth Engine (assumes you have a proper config module)
initialize_earth_engine()

class ESRILULCDataProcessor:
    def __init__(self, params: Dict[str, Any]):
        """
        Initialize ESRILULCDataProcessor with parameters.
        
        Args:
            params (Dict[str, Any]): Dictionary containing:
                - geojson_path (str): Path to GeoJSON file with district boundaries.
                Optionally, you can add keys 'start_year' and 'end_year'
                to limit the processing range (default is 2017 to 2023).
        """
        self.params = params
        self.CONFIG = {
            'ESRI_LULC_COLLECTION': 'projects/sat-io/open-datasets/landcover/ESRI_Global-LULC_10m_TS',
            'SCALE': 10,  # 10 meter resolution for ESRI LULC data.
            'MAX_PIXELS': 1e13,
            'TILE_SCALE': 4,
        }
        self.GEOJSON_PATH = params.get('geojson_path', '../../boundaries/datasets/maharashtra_districts.geojson')
        self.start_year = params.get('start_year', 2017)
        self.end_year = params.get('end_year', 2023)
        
        # Define the remapping parameters.
        # Original class values: [1,2,4,5,7,8,9,10,11] -> remapped to [1,2,3,4,5,6,7,8,9]
        self.ORIG_VALUES = [1, 2, 4, 5, 7, 8, 9, 10, 11]
        self.REMAPPED_VALUES = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        
        # Mapping from remapped numeric values to human‐readable class names.
        self.CLASS_MAP = {
            1: 'Water',
            2: 'Trees',
            3: 'Flooded_Vegetation',
            4: 'Crops',
            5: 'Built_Area',
            6: 'Bare_Ground',
            7: 'Snow_Ice',
            8: 'Clouds',
            9: 'Rangeland'
        }
    
    def _load_districts(self) -> List[Dict]:
        """Load district geometries from the GeoJSON file."""
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
    
    def _get_lulc_data_for_year(self, district: Dict, year: int) -> Dict:
        """
        Get the land cover measurements for a district for a given year.
        
        Args:
            district (Dict): Dictionary with keys 'name' and 'geometry'.
            year (int): Year for which to extract the measurement.
            
        Returns:
            Dict: A dictionary containing the district name, year, measurement ID,
                  dataset information, and pixel counts for each land cover class.
        """
        try:
            # Define the start and end dates for the year.
            year_start = f"{year}-01-01"
            year_end = f"{year}-12-31"
            
            # Filter the image collection to the given year and mosaic to get a single image.
            collection = ee.ImageCollection(self.CONFIG['ESRI_LULC_COLLECTION']) \
                .filterDate(year_start, year_end)
            
            # Mosaic the collection and apply the remapping.
            image = collection.mosaic().remap(self.ORIG_VALUES, self.REMAPPED_VALUES)
            
            # Compute the frequency histogram over the district geometry.
            # The result is a dictionary mapping remapped values (as strings) to pixel counts.
            histogram = image.reduceRegion(
                reducer=ee.Reducer.frequencyHistogram(),
                geometry=district['geometry'],
                scale=self.CONFIG['SCALE'],
                maxPixels=self.CONFIG['MAX_PIXELS'],
                tileScale=self.CONFIG['TILE_SCALE']
            ).getInfo()
            
            # The histogram is usually under the first band key.
            # Assume the image has a single band; get the first key.
            band_key = list(histogram.keys())[0] if histogram else None
            hist = histogram.get(band_key, {}) if band_key else {}
            
            measurement_id = str(uuid.uuid4())
            result = {
                'district_name': district['name'],
                'measurement_id': measurement_id,
                'year': year,
                'dataset': 'ESRI 10m Annual Land Cover'
            }
            
            # Add pixel counts for each class.
            # The keys in hist are strings representing the remapped integer values.
            for remapped_val, class_name in self.CLASS_MAP.items():
                count = int(hist.get(str(remapped_val), 0))
                result[class_name] = count
                # If desired, you could convert pixel counts to area (each pixel = 10x10 m = 100 m^2)
                # e.g., result[class_name + '_area_m2'] = count * 100
                
            return result
        except Exception as e:
            print(f"Error getting LULC data for {district['name']} in year {year}: {str(e)}")
            return {}
    
    def process_data(self) -> pd.DataFrame:
        """Process ESRI LULC data for all districts over annual intervals and return a DataFrame."""
        try:
            # Create a list of years to process.
            years = list(range(self.start_year, self.end_year + 1))
            print(f"Processing years: {years}")
            
            # Load district geometries from the GeoJSON file.
            districts = self._load_districts()
            print(f"Loaded {len(districts)} districts")
            
            all_data = []
            print(f"Processing data for {len(districts)} districts over {len(years)} years")
            
            # Use ThreadPoolExecutor to process each district-year combination concurrently.
            with ThreadPoolExecutor() as executor:
                futures = []
                for district in districts:
                    for year in years:
                        future = executor.submit(self._get_lulc_data_for_year, district, year)
                        futures.append(future)
                
                # Gather results.
                for future in futures:
                    result = future.result()
                    if result:  # Only add valid results.
                        all_data.append(result)
            
            df = pd.DataFrame(all_data)
            return df
        except Exception as e:
            print(f"Error in process_data: {str(e)}")
            return pd.DataFrame()
    
    def export_to_csv(self, filename: str = 'datasets/esri_lulc_measurements.csv'):
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
        'start_year': 2017,
        'end_year': 2023,
        'geojson_path': '../../boundaries/datasets/maharashtra_districts.geojson'
    }
    
    processor = ESRILULCDataProcessor(params)
    processor.export_to_csv()
