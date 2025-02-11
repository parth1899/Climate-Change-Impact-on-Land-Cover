import ee
import pandas as pd
from typing import List, Dict, Any, Optional
import json
from concurrent.futures import ThreadPoolExecutor
from config import initialize_earth_engine

class NO2DataProcessor:
    def __init__(self, params: Dict[str, Any]):
        """
        Initialize NO2DataProcessor with parameters.
        
        Args:
            params (Dict[str, Any]): Dictionary containing:
                - years (List[int]): List of years to analyze
                - region (str): Region name to analyze
                - levels (List[str]): List of NO2 levels to analyze ('low', 'medium', 'high')
        """
        # Initialize Earth Engine
        initialize_earth_engine()
        
        self.params = params
        self.CONFIG = {
            'NO2_COLLECTION': 'COPERNICUS/S5P/NRTI/L3_NO2',
            'SCALE': 1000,  # meters
            'MAX_PIXELS': 1e13,
            'TILE_SCALE': 4,
        }
        
        self.GEOJSON_PATH = 'Boundaries/stateBoundaries.geojson'
        
        # Define NO2 concentration thresholds (in mol/m^2)
        # Using large number instead of infinity for Earth Engine compatibility
        # self.NO2_LEVELS = {
        #     'low': [0, 0.00002],
        #     'medium': [0.00002, 0.00004],
        #     'high': [0.00004, 1.0]  # Using 1.0 as max value instead of infinity
        # }

        self.NO2_LEVELS = {
            'low': [0, 0.000055],  # Up to 0.000055
            'medium': [0.000055, 0.000060],  # 0.000055 to 0.000060
            'high': [0.000060, 0.001]  # Above 0.000060
        }

    def _get_region_geometry(self, region: str) -> ee.Geometry:
        """Get geometry for a region from GeoJSON file."""
        try:
            with open(self.GEOJSON_PATH, 'r') as f:
                geojson_data = json.load(f)
            
            region_feature = next(
                (feature for feature in geojson_data['features'] 
                if feature['properties']['shapeName'] == region),
                None
            )
            
            if region_feature is None:
                raise ValueError(f"Region not found: {region}")
                
            coords = region_feature['geometry']['coordinates']
            geom_type = region_feature['geometry']['type']
            
            if geom_type == 'MultiPolygon':
                return ee.Geometry.MultiPolygon(coords)
            elif geom_type == 'Polygon':
                return ee.Geometry.Polygon(coords)
            else:
                raise ValueError(f"Unsupported geometry type: {geom_type}")
        except Exception as e:
            raise ValueError(f"Error loading region geometry: {str(e)}")

    def _calculate_no2_stats(self, geometry: ee.Geometry, year: int, level: str) -> Dict[str, float]:
        """Calculate NO2 statistics for a specific level and geometry"""
        try:
            start_date = ee.Date.fromYMD(year, 1, 1)
            end_date = ee.Date.fromYMD(year + 1, 1, 1)
            
            # Get NO2 collection for the year
            collection = ee.ImageCollection(self.CONFIG['NO2_COLLECTION']) \
                .filterDate(start_date, end_date) \
                .select('NO2_column_number_density')
            
            # Calculate mean NO2 concentration
            mean_image = collection.mean()
            
            # Create mask for the specified level
            min_val, max_val = self.NO2_LEVELS[level]
            
            # Using ee.Number to ensure proper type conversion
            min_ee = ee.Number(min_val)
            max_ee = ee.Number(max_val)
            
            level_mask = mean_image.gte(min_ee).And(mean_image.lt(max_ee))
            masked_image = mean_image.updateMask(level_mask)
            
            # Calculate statistics
            stats = masked_image.reduceRegion(
                reducer=ee.Reducer.mean().combine(
                    ee.Reducer.stdDev(), None, True
                ).combine(
                    ee.Reducer.count(), None, True
                ),
                geometry=geometry,
                scale=self.CONFIG['SCALE'],
                maxPixels=self.CONFIG['MAX_PIXELS'],
                tileScale=self.CONFIG['TILE_SCALE']
            ).getInfo()
            
            return {
                'mean': stats.get('NO2_column_number_density_mean', 0),
                'std_dev': stats.get('NO2_column_number_density_stdDev', 0),
                'pixel_count': stats.get('NO2_column_number_density_count', 0)
            }
        except Exception as e:
            print(f"Error calculating NO2 stats for year {year}, level {level}: {str(e)}")
            return {
                'mean': 0,
                'std_dev': 0,
                'pixel_count': 0
            }

    def process_data(self) -> pd.DataFrame:
        """Process NO2 data and return DataFrame"""
        try:
            data = []
            geometry = self._get_region_geometry(self.params['region'])
            
            with ThreadPoolExecutor() as executor:
                futures = []
                for year in self.params['years']:
                    for level in self.params['levels']:
                        future = executor.submit(
                            self._calculate_no2_stats, geometry, year, level
                        )
                        futures.append((year, level, future))

                for year, level, future in futures:
                    try:
                        stats = future.result()
                        data.append({
                            'region': self.params['region'],
                            'year': year,
                            'level': level,
                            'mean_no2': stats['mean'],
                            'std_dev_no2': stats['std_dev'],
                            'pixel_count': stats['pixel_count']
                        })
                    except Exception as e:
                        print(f"Error processing data for year {year}, level {level}: {str(e)}")
                        continue

            return pd.DataFrame(data)
        except Exception as e:
            print(f"Error in process_data: {str(e)}")
            return pd.DataFrame()

    @staticmethod
    def get_level_colors() -> Dict[str, str]:
        """Return the color mapping for NO2 levels"""
        return {
            'high': 'red',
            'medium': 'green',
            'low': 'blue'
        }