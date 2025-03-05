import ee
import geemap
import json
import logging
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from config import initialize_earth_engine

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class OzoneMapProcessor:
    def __init__(self, selected_regions, start_year, end_year):
        # Initialize Earth Engine
        initialize_earth_engine()
        self.selected_regions = selected_regions
        self.start_year = int(start_year)
        self.end_year = int(end_year)
        # Visualization parameters for ozone – adjust as needed
        self.visualization_params = {
            "bands": ["O3_column_number_density"],
            "min": 0.12,
            "max": 0.15,
            "palette": ['black', 'blue', 'purple', 'cyan', 'green', 'yellow', 'red']
        }
        # Sentinel-5P Ozone dataset collection
        self.collection = "COPERNICUS/S5P/NRTI/L3_O3"
        # Path to the single combined GeoJSON file
        self.geojson_path = "boundaries/datasets/ADM4.geojson"
        try:
            with open(self.geojson_path, 'r') as f:
                self.geojson_data = json.load(f)
        except Exception as e:
            logging.error(f"Error loading GeoJSON file: {str(e)}")
            raise
        
        # Define parameters for numerical reduction.
        self.SCALE = 1113
        self.MAX_PIXELS = 1e13
        self.TILE_SCALE = 4

    def _filter_geojson(self):
        """Filter the combined GeoJSON to include only the selected regions."""
        filtered_features = []
        for region in self.selected_regions:
            if isinstance(region, str):
                found = False
                for feature in self.geojson_data.get("features", []):
                    if feature["properties"].get("shapeName") == region:
                        filtered_features.append(feature)
                        found = True
                        logging.info(f"Found geometry for region: {region}")
                        break
                if not found:
                    logging.warning(f"Region not found in GeoJSON: {region}")
            elif isinstance(region, dict):
                logging.info("Processing custom region geometry")
                filtered_features.append({
                    "type": "Feature",
                    "properties": {"shapeName": "Custom Region"},
                    "geometry": region
                })
            else:
                logging.warning(f"Invalid region format: {region}")
        return {"type": "FeatureCollection", "features": filtered_features}

    def _generate_monthly_intervals(self):
        """
        Generate monthly intervals between start_year and end_year.
        Each interval is a tuple: (year, month, interval_start, interval_end)
        """
        intervals = []
        for year in range(self.start_year, self.end_year + 1):
            for month in range(1, 3):
                start_dt = datetime(year, month, 1)
                # End of month: subtract one second from the first day of next month
                next_month = start_dt + relativedelta(months=1)
                end_dt = next_month - timedelta(seconds=1)
                interval_start = start_dt.strftime('%Y-%m-%dT%H:%M:%SZ')
                interval_end = end_dt.strftime('%Y-%m-%dT%H:%M:%SZ')
                intervals.append((year, month, interval_start, interval_end))
        return intervals

    def generate_urls(self):
        """
        For each region (from filtered GeoJSON) and for every monthly interval,
        create a composite (mean) image for the ozone data, clip it to the region,
        generate a tile URL, and compute the numerical mean of the 
        O3_column_number_density.
        
        Returns:
            urls (dict): Dictionary mapping a key "region - YYYY-MM" to a tile URL.
            stats (dict): Dictionary mapping the same key to the mean O3_column_number_density.
            filtered_geojson (dict): GeoJSON with only the selected region features.
        """
        filtered_geojson = self._filter_geojson()
        urls = {}
        stats = {}
        intervals = self._generate_monthly_intervals()
        
        for feature in filtered_geojson.get("features", []):
            region_name = feature["properties"].get("shapeName", "Custom Region")
            geometry = ee.Geometry(feature["geometry"])
            
            for year, month, interval_start, interval_end in intervals:
                key = f"{region_name} - {year}-{month:02d}"
                logging.info(f"Processing {key}")
                try:
                    # Filter the ozone collection over the monthly interval and select the desired band
                    collection = ee.ImageCollection(self.collection) \
                        .filterDate(interval_start, interval_end) \
                        .select("O3_column_number_density")
                    # Compute the monthly composite using mean()
                    image = collection.mean()
                    # Clip the image to the region's geometry
                    clipped_image = image.clip(geometry)
                    # Generate a tile layer (the layer name includes the region and month)
                    tile_layer = geemap.ee_tile_layer(
                        clipped_image,
                        self.visualization_params,
                        f"{region_name} ({year}-{month:02d})"
                    )
                    # Extract the URL for the tile layer
                    url = tile_layer.url_format
                    urls[key] = url

                    # Compute numerical stats (mean value) over the region
                    stats_result = clipped_image.reduceRegion(
                        reducer=ee.Reducer.mean(),
                        geometry=geometry,
                        scale=self.SCALE,
                        maxPixels=self.MAX_PIXELS,
                        tileScale=self.TILE_SCALE
                    ).getInfo()
                    o3_mean = stats_result.get("O3_column_number_density", None)
                    stats[key] = o3_mean
                    
                except Exception as e:
                    logging.error(f"Error processing {key}: {str(e)}")
                    continue
        return urls, stats, filtered_geojson

def ozone_main(selected_regions, start_year, end_year):
    """
    Main function for generating ozone map URLs and numerical statistics.
    
    Args:
        selected_regions (list): List of region names (str) or geometries (dict).
        start_year (int or str): The starting year.
        end_year (int or str): The ending year.
    
    Returns:
        tuple: (urls, stats, legends, filtered_geojson, selected_regions)
    """
    try:
        processor = OzoneMapProcessor(selected_regions, start_year, end_year)
        urls, stats, filtered_geojson = processor.generate_urls()
        # For the legend, here we simply return the first color of the palette
        legends = {"Ozone": processor.visualization_params["palette"][0]}
        return urls, stats, legends, filtered_geojson, selected_regions
    except Exception as e:
        logging.error(f"Error in ozone_main: {str(e)}")
        raise

# Example usage:
# if __name__ == "__main__":
#     selected_regions = ['Pune', 'Ahmadnagar']  # or custom geometries as dicts
#     start_year = 2020
#     end_year = 2020
#     urls, stats, legends, geojson_data, selected_regions = ozone_main(selected_regions, start_year, end_year)
#     print("Tile URLs:", urls)
#     print("Stats:", stats)
