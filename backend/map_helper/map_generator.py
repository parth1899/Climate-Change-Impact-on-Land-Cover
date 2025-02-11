import ee
import geemap
import json

from config import initialize_earth_engine

class NO2Processor:
    def __init__(self):
        initialize_earth_engine()
        
        # Predefined NO2 concentration classes
        self.predefined_classes = {
            'low': 1,
            'medium': 2,
            'high': 3
        }
        
        # Visualization parameters for NO2 concentration classes
        self.visualization_params = {
            'low': {
                'bands': ['NO2_column_number_density'],
                'palette': ['blue'],
                'min': 0,
                'max': 0.00005
            },
            'medium': {
                'bands': ['NO2_column_number_density'],
                'palette': ['green'],
                'min': 0.00005,
                'max': 0.0001
            },
            'high': {
                'bands': ['NO2_column_number_density'],
                'palette': ['red'],
                'min': 0.0001,
                'max': 0.0002
            }
        }

    def _get_no2_dataset(self, year: int, class_name: str) -> tuple:
        """
        Retrieve and process NO2 dataset for a specific year and class
        """
        # Filter NO2 collection by date
        dataset = ee.ImageCollection("COPERNICUS/S5P/OFFL/L3_NO2") \
            .filterDate(f"{year}-01-01", f"{year}-12-31") \
            .select('NO2_column_number_density')
        
        # Compute mean image
        image = dataset.mean()
        
        # Mask image based on concentration thresholds
        thresholds = {
            'low': (0, 0.00005),
            'medium': (0.00005, 0.0001),
            'high': (0.0001, 0.0002)
        }
        
        min_val, max_val = thresholds[class_name]
        masked_image = image.updateMask(
            image.gte(min_val).And(image.lt(max_val))
        )
        
        return masked_image, self.visualization_params[class_name]

    def generate_urls(
        self, 
        selected_years, 
        selected_classes, 
        region_name, 
        geojson_path
    ):
        """
        Generate tile URLs for NO2 concentration maps
        """
        # Load GeoJSON and find the specific region
        with open(geojson_path, 'r') as f:
            geojson_data = json.load(f)
        
        # Find the feature for the specified region
        region_feature = next(
            (feature for feature in geojson_data['features'] 
             if feature['properties']['shapeName'].lower() == region_name.lower()),
            None
        )
        
        if not region_feature:
            raise ValueError(f"Region {region_name} not found in the GeoJSON")
        
        # Convert region geometry to Earth Engine Geometry
        region_geometry = ee.Geometry(region_feature['geometry'])
        
        # Store generated URLs
        urls = {}
        
        for year in selected_years:
            for class_name in selected_classes:
                # Generate new URL
                image, vis_params = self._get_no2_dataset(year, class_name)
                clipped_image = image.clip(region_geometry)
                
                tile_layer = geemap.ee_tile_layer(
                    clipped_image,
                    vis_params,
                    f"NO2 {class_name.capitalize()} ({year})"
                )
                url = tile_layer.url_format
                
                # Store URL
                key = f"{region_name} - {year} - {class_name}"
                urls[key] = url
        
        return urls

def generate_no2_maps(
    selected_years, 
    selected_classes, 
    region_name, 
    geojson_path='Boundaries/stateBoundaries.geojson'
):
    """
    Main function to generate NO2 maps
    """
    processor = NO2Processor()
    
    # Generate map URLs
    urls = processor.generate_urls(
        selected_years,
        selected_classes,
        region_name,
        geojson_path
    )
    
    # Generate legends
    legends = {
        class_name: processor.visualization_params[class_name]["palette"][0] 
        for class_name in selected_classes
    }
    
    return {
        "map_urls": urls,
        "legends": legends
    }