import ee
import geemap
import json
import logging
from datetime import datetime
from config import initialize_earth_engine

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class LandCoverMapProcessor:
    def __init__(self, selected_regions, start_year, end_year):
        # Initialize Earth Engine
        initialize_earth_engine()
        self.selected_regions = selected_regions
        self.start_year = int(start_year)
        self.end_year = int(end_year)
        # Visualization parameters for land cover
        self.visualization_params = {
            "min": 1,
            "max": 9,
            "palette": [
                "#1A5BAB",  # Water
                "#358221",  # Trees
                "#87D19E",  # Flooded Vegetation
                "#FFDB5C",  # Crops
                "#ED022A",  # Built Area
                "#EDE9E4",  # Bare Ground
                "#F2FAFF",  # Snow/Ice
                "#C8C8C8",  # Clouds
                "#C6AD8D"   # Rangeland
            ]
        }
        # ESRI 10m Annual Land Cover dataset collection
        self.collection = "projects/sat-io/open-datasets/landcover/ESRI_Global-LULC_10m_TS"
        # Path to the combined GeoJSON file for region boundaries
        self.geojson_path = "../../boundaries/datasets/ADM4.geojson"
        try:
            with open(self.geojson_path, 'r') as f:
                self.geojson_data = json.load(f)
        except Exception as e:
            logging.error(f"Error loading GeoJSON file: {str(e)}")
            raise
        
        # Define parameters for numerical reduction.
        # For 10m resolution data, set scale to 10.
        self.SCALE = 10
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

    def _generate_yearly_intervals(self):
        """
        Generate annual intervals between start_year and end_year.
        Each interval is a tuple: (year, interval_start, interval_end)
        """
        intervals = []
        for year in range(self.start_year, self.end_year + 1):
            interval_start = f"{year}-01-01"
            interval_end = f"{year}-12-31"
            intervals.append((year, interval_start, interval_end))
        return intervals

    def _remap_image(self, image):
        """
        Remap the original land cover classes:
            From [1, 2, 4, 5, 7, 8, 9, 10, 11]
            To   [1, 2, 3, 4, 5, 6, 7, 8, 9]
        """
        return image.remap([1, 2, 4, 5, 7, 8, 9, 10, 11], [1, 2, 3, 4, 5, 6, 7, 8, 9])

    def generate_urls(self):
        """
        For each region (from filtered GeoJSON) and for every annual interval,
        create a composite image (mosaic) for the land cover data, apply remapping,
        clip it to the region, generate a tile URL, and compute a statistical summary
        (mode) of the land cover classification.
        
        Returns:
            urls (dict): Dictionary mapping "region - YYYY" to a tile URL.
            stats (dict): Dictionary mapping the same key to the mode of land cover.
            filtered_geojson (dict): GeoJSON with only the selected region features.
        """
        filtered_geojson = self._filter_geojson()
        urls = {}
        stats = {}
        intervals = self._generate_yearly_intervals()
        
        for feature in filtered_geojson.get("features", []):
            region_name = feature["properties"].get("shapeName", "Custom Region")
            geometry = ee.Geometry(feature["geometry"])
            
            for year, interval_start, interval_end in intervals:
                key = f"{region_name} - {year}"
                logging.info(f"Processing {key}")
                try:
                    # Filter the land cover collection for the annual interval
                    collection = ee.ImageCollection(self.collection) \
                        .filterDate(interval_start, interval_end)
                    # Mosaic the images to form a single composite for the year
                    image = collection.mosaic()
                    # Apply the remapping function to standardize class values
                    remapped_image = self._remap_image(image)
                    # Clip the image to the region's geometry
                    clipped_image = remapped_image.clip(geometry)
                    # Generate a tile layer for visualization
                    tile_layer = geemap.ee_tile_layer(
                        clipped_image,
                        self.visualization_params,
                        f"{region_name} ({year})"
                    )
                    # Extract the URL for the tile layer
                    url = tile_layer.url_format
                    urls[key] = url

                    # Compute the mode (most frequent class) over the region.
                    stats_result = clipped_image.reduceRegion(
                        reducer=ee.Reducer.mode(),
                        geometry=geometry,
                        scale=self.SCALE,
                        maxPixels=self.MAX_PIXELS,
                        tileScale=self.TILE_SCALE
                    ).getInfo()
                    stats[key] = stats_result
                except Exception as e:
                    logging.error(f"Error processing {key}: {str(e)}")
                    continue
        return urls, stats, filtered_geojson

def landcover_main(selected_regions, start_year, end_year):
    """
    Main function for generating land cover map tile URLs and statistics.
    
    Args:
        selected_regions (list): List of region names (str) or geometries (dict).
        start_year (int or str): The starting year (>= 2017).
        end_year (int or str): The ending year (<= 2023).
    
    Returns:
        tuple: (urls, stats, legends, filtered_geojson, selected_regions)
    """
    try:
        processor = LandCoverMapProcessor(selected_regions, start_year, end_year)
        urls, stats, filtered_geojson = processor.generate_urls()
        # Create legend as a mapping of class names to their respective colors
        class_names = [
            "Water",
            "Trees",
            "Flooded Vegetation",
            "Crops",
            "Built Area",
            "Bare Ground",
            "Snow/Ice",
            "Clouds",
            "Rangeland"
        ]
        colors = processor.visualization_params["palette"]
        legends = dict(zip(class_names, colors))
        return urls, stats, legends, filtered_geojson, selected_regions
    except Exception as e:
        logging.error(f"Error in landcover_main: {str(e)}")
        raise

# Example usage:
# if __name__ == "__main__":
#     selected_regions = ['Pune', 'Ahmadnagar']  # or use custom geometries (dicts)
#     start_year = 2017
#     end_year = 2023
#     urls, stats, legends, geojson_data, selected_regions = landcover_main(selected_regions, start_year, end_year)
#     print("Tile URLs:", urls)
#     print("Stats:", stats)
#     print("Legends:", legends)
