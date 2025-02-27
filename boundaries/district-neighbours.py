import geopandas as gpd
import json

# Read the GeoJSON file
gdf = gpd.read_file('datasets/maharashtra_districts.geojson')

# Initialize a dictionary to store neighbors.
neighbors_dict = {}

# Loop through each district feature.
for idx, row in gdf.iterrows():
    current_district = row['shapeName_1']
    current_geom = row.geometry
    current_neighbors = []
    
    # Compare with every other district.
    for idx2, row2 in gdf.iterrows():
        if idx == idx2:
            continue  # Skip self
        
        other_district = row2['shapeName_1']
        other_geom = row2.geometry
        
        # Check if the geometries touch.
        if current_geom.touches(other_geom):
            current_neighbors.append(other_district)
    
    neighbors_dict[current_district] = current_neighbors

# Save the dictionary to a JSON file.
with open('district_neighbors.json', 'w') as json_file:
    json.dump(neighbors_dict, json_file, indent=4)

print("Neighbors saved to 'district_neighbors.json'")
