import geopandas as gpd

# Load the districts GeoJSON
districts = gpd.read_file("geoBoundaries-IND-ADM2.geojson")

# Load Maharashtra boundary GeoJSON
maharashtra_boundary = gpd.read_file("maharashtra_boundary.geojson")

# Ensure both layers have the same CRS (Coordinate Reference System)
districts = districts.to_crs(maharashtra_boundary.crs)

# Spatial intersection: Get districts within Maharashtra boundary
maharashtra_districts = gpd.overlay(districts, maharashtra_boundary, how="intersection")

# Save the result as a new GeoJSON file
maharashtra_districts.to_file("maharashtra_districts.geojson", driver="GeoJSON")

print("Maharashtra districts extracted and saved to maharashtra_districts.geojson")
