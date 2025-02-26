import geopandas as gpd
import folium

# Load GeoJSON files
districts = gpd.read_file("datasets/geoBoundaries-IND-ADM2.geojson")
maharashtra_boundary = gpd.read_file("datasets/maharashtra_boundary.geojson")
maharashtra_districts = gpd.read_file("datasets/maharashtra_districts.geojson")

# Convert CRS to EPSG:4326 (if not already in this format)
districts = districts.to_crs(epsg=4326)
maharashtra_boundary = maharashtra_boundary.to_crs(epsg=4326)
maharashtra_districts = maharashtra_districts.to_crs(epsg=4326)

# Get the centroid of Maharashtra for the initial map focus
# Convert to a projected CRS (e.g., UTM zone 43N for Maharashtra)
maharashtra_boundary_projected = maharashtra_boundary.to_crs(epsg=32643)

# Compute centroid in projected CRS, then transform back
maharashtra_center_projected = maharashtra_boundary_projected.geometry.centroid.iloc[0]

# Convert back to EPSG:4326 for mapping
maharashtra_center = gpd.GeoSeries(maharashtra_center_projected, crs=32643).to_crs(epsg=4326).iloc[0]

m = folium.Map(location=[maharashtra_center.y, maharashtra_center.x], zoom_start=6, tiles="cartodbpositron")

# Add Districts Layer (Full India)
folium.GeoJson(
    districts,
    name="All Districts (India)",
    style_function=lambda x: {"color": "gray", "weight": 0.5, "fillOpacity": 0.1}
).add_to(m)

# Add Maharashtra Boundary Layer
folium.GeoJson(
    maharashtra_boundary,
    name="Maharashtra Boundary",
    style_function=lambda x: {"color": "blue", "weight": 2, "fillOpacity": 0}
).add_to(m)

# Add Maharashtra Districts Layer (Extracted)
folium.GeoJson(
    maharashtra_districts,
    name="Maharashtra Districts",
    style_function=lambda x: {"color": "red", "weight": 1, "fillOpacity": 0.3}
).add_to(m)

# Add Layer Control to Toggle Layers
folium.LayerControl().add_to(m)

# Save and display the map
m.save("maharashtra_districts_map2.html")
print("Map saved as maharashtra_districts_map.html. Open it in a browser.")
