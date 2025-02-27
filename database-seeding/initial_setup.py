import csv
import json
from neo4j_connection import Neo4jConnection
from models import District

def load_districts(file_path: str):
    districts = []
    with open(file_path, "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            districts.append(
                District(
                    district_id=row["district_id"],
                    name=row["District_name"],
                    centroid_latitude=float(row["centroid_latitude"]),
                    centroid_longitude=float(row["centroid_longitude"]),
                    area=float(row["area"])
                )
            )
    return districts

def create_district_node(conn: Neo4jConnection, district: District):
    query = """
    CREATE (d:District {
      district_id: $district_id,
      name: $name,
      centroid_latitude: $centroid_latitude,
      centroid_longitude: $centroid_longitude,
      area: $area
    })
    """
    params = {
        "district_id": district.district_id,
        "name": district.name,
        "centroid_latitude": district.centroid_latitude,
        "centroid_longitude": district.centroid_longitude,
        "area": district.area
    }
    conn.query(query, parameters=params)

def create_neighbour_relationships_from_json(conn: Neo4jConnection, json_file_path: str):
    with open(json_file_path, "r", encoding="utf-8") as f:
        neighbours_data = json.load(f)
    
    for district, neighbours in neighbours_data.items():
        for neighbour in neighbours:
            query = """
            MATCH (d:District {name: $district_name}), (n:District {name: $neighbour_name})
            MERGE (d)-[:NEIGHBOR_OF]->(n)
            """
            params = {"district_name": district, "neighbour_name": neighbour}
            conn.query(query, parameters=params)

def main():
    # Connect to Neo4j.
    conn = Neo4jConnection()

    # Create District nodes.
    districts = load_districts("../boundaries/datasets/maharashtra_districts_details.csv")
    for district in districts:
        create_district_node(conn, district)

    # Create NEIGHBOR_OF relationships based on JSON data.
    create_neighbour_relationships_from_json(conn, "../boundaries/datasets/district_neighbours.json")

    # Close the connection.
    conn.close()

if __name__ == "__main__":
    main()
