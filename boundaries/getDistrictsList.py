import json

# Load the GeoJSON file
with open("maharashtra_districts.geojson", "r", encoding="utf-8") as f:
    data = json.load(f)

# Extract district names
district_names = [feature["properties"]["shapeName_1"] for feature in data["features"]]

# Save to a text file
with open("maharashtra_district_names.txt", "w", encoding="utf-8") as f:
    for name in district_names:
        f.write(name + "\n")

print("District names saved to maharashtra_district_names.txt")
