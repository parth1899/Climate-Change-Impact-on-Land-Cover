import json

# Load the GeoJSON file
with open("geoBoundaries-IND-ADM1 (1).geojson", "r", encoding="utf-8") as f:
    data = json.load(f)

# Extract district names
states_names = [feature["properties"]["shapeName"] for feature in data["features"]]

# Save to a text file
with open("states_and_ut_names.txt", "w", encoding="utf-8") as f:
    for name in states_names:
        f.write(name + "\n")

print("District names saved to states_and_ut_names.txt")
