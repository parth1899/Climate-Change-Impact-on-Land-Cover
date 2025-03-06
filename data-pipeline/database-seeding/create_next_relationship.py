import csv
from collections import defaultdict
from datetime import datetime
from neo4j_connection import Neo4jConnection

# Parsing functions for timestamps.

def parse_full_timestamp(timestamp_str: str) -> datetime:
    """
    Parses a timestamp of the format:
      "2018-10-16T11:02:44 to 2018-10-23T11:02:44"
    Returns a datetime for the first (start) date.
    """
    try:
        start_part = timestamp_str.split(" to ")[0]
        return datetime.strptime(start_part, "%Y-%m-%dT%H:%M:%S")
    except Exception as e:
        # print(f"Error parsing full timestamp '{timestamp_str}': {e}")
        return None

def parse_year_timestamp(timestamp_str: str) -> int:
    """
    Parses a timestamp that is simply a year (e.g. "2021").
    """
    try:
        return int(timestamp_str)
    except Exception as e:
        # print(f"Error parsing year timestamp '{timestamp_str}': {e}")
        return None

def create_next_relationships_for_label(conn: Neo4jConnection, label: str, parse_timestamp_func):
    """
    For a given measurement label (node type), retrieve all measurements,
    group them by district (region), sort them by timestamp (using the given parse function),
    and create a NEXT relationship from each measurement to the next one.
    """
    # Query to get measurement nodes for this type.
    query = f"""
    MATCH (m:{label})
    RETURN m.measurement_id AS measurement_id, m.region AS region, m.timestamp AS timestamp
    """
    records = conn.query(query)
    
    # Group measurements by district/region.
    measurements_by_region = defaultdict(list)
    for record in records:
        measurement_id = record['measurement_id']
        region = record['region']
        ts_str = record['timestamp']
        parsed_ts = parse_timestamp_func(ts_str)
        if parsed_ts is not None:
            measurements_by_region[region].append((measurement_id, parsed_ts))
    
    # For each region, sort the measurements by timestamp and create NEXT relationships.
    for region, meas_list in measurements_by_region.items():
        # Sort by the parsed timestamp.
        meas_list.sort(key=lambda x: x[1])
        for i in range(len(meas_list) - 1):
            from_id = meas_list[i][0]
            to_id = meas_list[i + 1][0]
            rel_query = f"""
            MATCH (m1:{label} {{measurement_id: $from_id}}), (m2:{label} {{measurement_id: $to_id}})
            MERGE (m1)-[:NEXT]->(m2)
            """
            conn.query(rel_query, parameters={"from_id": from_id, "to_id": to_id})
            # print(f"Created NEXT relationship from {from_id} to {to_id} for region {region}")

def create_all_next_relationships():
    """
    Create NEXT relationships for all measurement types.
    """
    conn = Neo4jConnection()
    try:
        # For CO, Ozone, and Aerosol, use the full timestamp parser.
        for label in ["CO_Measurement", "Ozone_Measurement", "Aerosol_AI_Measurement"]:
            # print(f"Processing NEXT relationships for {label}...")
            create_next_relationships_for_label(conn, label, parse_full_timestamp)
        
        # For Land Cover measurements, use the year parser.
        # print("Processing NEXT relationships for LandCoverMeasurement...")
        create_next_relationships_for_label(conn, "LandCoverMeasurement", parse_year_timestamp)
    finally:
        conn.close()

if __name__ == "__main__":
    create_all_next_relationships()
