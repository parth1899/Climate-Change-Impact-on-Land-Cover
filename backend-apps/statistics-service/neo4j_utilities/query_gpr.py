from datetime import datetime
from neo4j_utilities.neo4j_connection import neo4j_connection

# Mapping of atmospheric measurement types to their corresponding Neo4j labels.
MEASUREMENT_TYPES = {
    "CO": "CO_Measurement",
    "Ozone": "Ozone_Measurement",
    "Aerosol": "Aerosol_AI_Measurement"
}

# Mapping from prediction target to the specific field we wish to predict.
TARGET_FIELD = {
    "CO": "CO_column_number_density",
    "Ozone": "O3_column_number_density",
    "Aerosol": "absorbing_aerosol_index"
}

def extract_valid_datetime(timestamp_str):
    """
    Extracts a valid datetime from a timestamp string.
    It first tries the ISO format "%Y-%m-%dT%H:%M:%S".
    If that fails and the string appears to be just a year (e.g., "2023"),
    it will try the "%Y" format.
    If the string contains a range (" to "), it extracts the first date.
    Returns None if no valid format is found.
    """
    try:
        return datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S").isoformat()
    except ValueError:
        pass

    if len(timestamp_str) == 4 and timestamp_str.isdigit():
        try:
            dt = datetime.strptime(timestamp_str, "%Y")
            return dt.isoformat()
        except ValueError:
            pass

    if " to " in timestamp_str:
        first_date = timestamp_str.split(" to ")[0]
        try:
            return datetime.strptime(first_date, "%Y-%m-%dT%H:%M:%S").isoformat()
        except ValueError:
            if len(first_date) == 4 and first_date.isdigit():
                try:
                    dt = datetime.strptime(first_date, "%Y")
                    return dt.isoformat()
                except ValueError:
                    pass
            return None

    return None

def get_measurements(district, start_date, end_date, prediction_target):
    """
    Fetches the requested atmospheric measurement for a given district within the provided date range.
    Returns:
      - timestamp (ISO string)
      - id (measurement id)
      - the target measurement field under its full name (e.g. "CO_column_number_density")
      - "parameter": the name of the measurement field.
    """
    if prediction_target not in MEASUREMENT_TYPES:
        raise ValueError("Invalid prediction_target. Choose from 'CO', 'Ozone', or 'Aerosol'.")
    measurement_type = MEASUREMENT_TYPES[prediction_target]
    target_field = TARGET_FIELD[prediction_target]

    query = f"""
    MATCH (d:District {{name: $district}})-[:HAS_MEASUREMENT]->(m:{measurement_type})
    WHERE m.timestamp >= $start_date AND m.timestamp <= $end_date
    RETURN substring(m.timestamp, 0, 19) AS timestamp,
           m.measurement_id AS id,
           m.{target_field} AS {target_field}
    ORDER BY timestamp
    """
    results = neo4j_connection.execute_query(query, {
        "district": district,
        "start_date": start_date,
        "end_date": end_date
    })
    output = []
    for record in results:
        ts = extract_valid_datetime(record["timestamp"])
        if ts:
            output.append({
                "timestamp": ts,
                "id": record["id"],
                target_field: record[target_field],
                "parameter": target_field
            })
    return output

def get_neighbor_measurements(district, start_date, end_date, prediction_target):
    """
    Fetches atmospheric measurement data for neighboring districts within the given date range.
    Returns, for each neighbor, the timestamp, id, and target field value.
    """
    if prediction_target not in MEASUREMENT_TYPES:
        raise ValueError("Invalid prediction_target. Choose from 'CO', 'Ozone', or 'Aerosol'.")
    measurement_type = MEASUREMENT_TYPES[prediction_target]
    target_field = TARGET_FIELD[prediction_target]

    query = f"""
    MATCH (d:District {{name: $district}})-[:NEIGHBOR_OF]->(n:District)-[:HAS_MEASUREMENT]->(m:{measurement_type})
    WHERE m.timestamp >= $start_date AND m.timestamp <= $end_date
    RETURN n.name AS neighbor_district,
           substring(m.timestamp, 0, 19) AS timestamp,
           m.measurement_id AS id,
           m.{target_field} AS {target_field}
    ORDER BY n.name, timestamp
    """
    results = neo4j_connection.execute_query(query, {
        "district": district,
        "start_date": start_date,
        "end_date": end_date
    })
    neighbors = {}
    for record in results:
        ts = extract_valid_datetime(record["timestamp"])
        if ts:
            entry = {
                "timestamp": ts,
                "id": record["id"],
                target_field: record[target_field],
                "parameter": target_field
            }
            neighbor_name = record["neighbor_district"]
            if neighbor_name not in neighbors:
                neighbors[neighbor_name] = []
            neighbors[neighbor_name].append(entry)
    return neighbors

def get_landcover_timeseries(district):
    """
    Retrieves the entire timeseries of landcover data for a given district.
    Returns only the relevant landcover parameters with descriptive keys.
    Relevant fields: water, trees, crops, built_area, bare_ground, rangeland.
    Uses a case-insensitive match on the 'region' property.
    """
    query = """
    MATCH (l:LandCoverMeasurement)
    WHERE toLower(l.region) = toLower($district)
    RETURN l.timestamp AS timestamp,
           l.measurement_id AS id,
           { water: l.Water, trees: l.Trees, crops: l.Crops, built_area: l.Built_Area,
             bare_ground: l.Bare_Ground, rangeland: l.Rangeland } AS parameters
    ORDER BY l.timestamp
    """
    results = neo4j_connection.execute_query(query, {"district": district})
    return [
        {"timestamp": extract_valid_datetime(record["timestamp"]),
         "id": record["id"],
         **record["parameters"]}
        for record in results if extract_valid_datetime(record["timestamp"])
    ]

def get_neighbor_landcover_timeseries(district):
    """
    Retrieves the entire timeseries of landcover data for all neighboring districts of a given district.
    Returns a dictionary keyed by neighbor district, each value being a list of measurement objects.
    """
    query = """
    MATCH (d:District {name: $district})-[:NEIGHBOR_OF]->(n:District)
    WITH collect(n.name) AS neighborNames
    MATCH (l:LandCoverMeasurement)
    WHERE l.region IN neighborNames
    RETURN l.region AS neighbor,
           l.timestamp AS timestamp,
           l.measurement_id AS id,
           { water: l.Water, trees: l.Trees, crops: l.Crops, built_area: l.Built_Area,
             bare_ground: l.Bare_Ground, rangeland: l.Rangeland } AS parameters
    ORDER BY l.region, l.timestamp
    """
    results = neo4j_connection.execute_query(query, {"district": district})
    neighbor_landcover = {}
    for record in results:
        ts = extract_valid_datetime(record["timestamp"])
        if ts:
            entry = {
                "timestamp": ts,
                "id": record["id"],
                **record["parameters"]
            }
            neighbor = record["neighbor"]
            if neighbor not in neighbor_landcover:
                neighbor_landcover[neighbor] = []
            neighbor_landcover[neighbor].append(entry)
    return neighbor_landcover
