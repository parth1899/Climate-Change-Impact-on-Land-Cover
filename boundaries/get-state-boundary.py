import json

# Load the GeoJSON file
with open("datasets/geoBoundaries-IND-ADM2.geojson", "r", encoding="utf-8") as f:
    data = json.load(f)

# Filter Maharashtra boundary
pune_boundary = [
    feature for feature in data["features"]
    if feature["properties"]["shapeName"] == "Pune"
]

# Create a new GeoJSON structure
pune_geojson = {
    "type": "FeatureCollection",
    "crs": data["crs"],  # Keep the same CRS
    "features": pune_boundary
}

# Save to a new GeoJSON file
with open("pune_boundary.geojson", "w", encoding="utf-8") as f:
    json.dump(pune_geojson, f, indent=4)

print("Pune boundary saved to pune_geojson.geojson")
