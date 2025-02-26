import geopandas as gpd

# 1. Read the GeoJSON file
gdf = gpd.read_file('datasets/maharashtra_districts.geojson')

# 2. Reproject the GeoDataFrame to a projected CRS for accurate area calculations.
# EPSG:3857 is used here, but you might want to choose an equal-area projection for India.
gdf_proj = gdf.to_crs(epsg=3857)

# 3. Calculate the area (in square meters)
gdf_proj['area'] = gdf_proj.geometry.area

# 4. Compute the centroid. This works for both Polygon and MultiPolygon.
# Note: For MultiPolygons, the centroid might lie outside the geometry.
gdf_proj['centroid'] = gdf_proj.geometry.centroid

# Alternatively, if you need a point guaranteed to lie within the geometry, use:
# gdf_proj['centroid'] = gdf_proj.geometry.representative_point()

# 5. Convert centroids back to WGS84 to obtain latitude and longitude.
centroids_wgs84 = gdf_proj['centroid'].to_crs(epsg=4326)
gdf_proj['centroid_longitude'] = centroids_wgs84.x
gdf_proj['centroid_latitude'] = centroids_wgs84.y

# 6. Prepare the final DataFrame with the required columns.
result_df = gdf_proj[['shapeName_1', 'shapeID_1', 'centroid_latitude', 'centroid_longitude', 'area']].copy()
result_df.rename(columns={'shapeName_1': 'District_name', 'shapeID_1': 'district_id'}, inplace=True)

# 7. Save the results to a CSV file.
result_df.to_csv('maharashtra_districts_details.csv', index=False)
