import json

# Load the GeoJSON file
with open("geoBoundaries-IND-ADM1 (1).geojson", "r", encoding="utf-8") as f:
    data = json.load(f)

# Filter Maharashtra boundary
maharashtra_boundary = [
    feature for feature in data["features"]
    if feature["properties"]["shapeName"] == "Maharashtra" or feature["properties"]["shapeISO"] == "IN-MH"
]

# Create a new GeoJSON structure
maharashtra_geojson = {
    "type": "FeatureCollection",
    "crs": data["crs"],  # Keep the same CRS
    "features": maharashtra_boundary
}

# Save to a new GeoJSON file
with open("maharashtra_boundary.geojson", "w", encoding="utf-8") as f:
    json.dump(maharashtra_geojson, f, indent=4)

print("Maharashtra boundary saved to maharashtra_boundary.geojson")
