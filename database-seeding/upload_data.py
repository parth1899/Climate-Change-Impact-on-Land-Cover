import csv
import json
from neo4j_connection import Neo4jConnection
from models import Measurement, District, Dataset
from config import Config

def safe_float(value, default=None):
    """
    Safely convert a string value to float.
    Returns default if value is empty or invalid.
    """
    try:
        return float(value) if value != "" else default
    except ValueError:
        return default

def load_measurements(file_path: str, missing_file: str = "missing_records.csv"):
    measurements = []
    missing_records = []
    numeric_fields = [
        "CO_column_number_density", "H2O_column_number_density", "cloud_height",
        "sensor_altitude", "sensor_azimuth_angle", "sensor_zenith_angle",
        "solar_azimuth_angle", "solar_zenith_angle"
    ]
    
    with open(file_path, "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row_number, row in enumerate(reader, start=1):
            # Check for missing numeric values in the record.
            if any(row.get(field, "").strip() == "" for field in numeric_fields):
                # Add row number and row data to the missing records list.
                missing_record = {"row_number": row_number}
                missing_record.update(row)
                missing_records.append(missing_record)
                continue

            measurements.append(
                Measurement(
                    measurement_id=row["measurement_id"],
                    region=row["district_name"],
                    timestamp=row["timestamp"],
                    dataset=row["dataset"],
                    CO_column_number_density=float(row["CO_column_number_density"]),
                    H2O_column_number_density=float(row["H2O_column_number_density"]),
                    cloud_height=float(row["cloud_height"]),
                    sensor_altitude=float(row["sensor_altitude"]),
                    sensor_azimuth_angle=float(row["sensor_azimuth_angle"]),
                    sensor_zenith_angle=float(row["sensor_zenith_angle"]),
                    solar_azimuth_angle=float(row["solar_azimuth_angle"]),
                    solar_zenith_angle=float(row["solar_zenith_angle"])
                )
            )
    
    # Write missing records to a CSV file if any records were skipped.
    if missing_records:
        with open(missing_file, "w", encoding="utf-8", newline="") as missing_csvfile:
            fieldnames = list(missing_records[0].keys())
            writer = csv.DictWriter(missing_csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(missing_records)
        print(f"Missing records written to {missing_file}")
    
    return measurements


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

def create_dataset_node(conn: Neo4jConnection, dataset: Dataset):
    query = """
    MERGE (d:Dataset {dataset_id: $dataset_id})
    SET d.name = $name,
        d.description = $description,
        d.temporal_coverage = $temporal_coverage,
        d.spatial_resolution = $spatial_resolution
    """
    params = {
        "dataset_id": dataset.dataset_id,
        "name": dataset.name,
        "description": dataset.description,
        "temporal_coverage": dataset.temporal_coverage,
        "spatial_resolution": dataset.spatial_resolution
    }
    conn.query(query, parameters=params)

def create_measurement_node(conn: Neo4jConnection, measurement: Measurement):
    query = """
    CREATE (m:Measurement {
      measurement_id: $measurement_id,
      region: $region,
      timestamp: $timestamp,
      dataset: $dataset,
      CO_column_number_density: $CO_column_number_density,
      H2O_column_number_density: $H2O_column_number_density,
      cloud_height: $cloud_height,
      sensor_altitude: $sensor_altitude,
      sensor_azimuth_angle: $sensor_azimuth_angle,
      sensor_zenith_angle: $sensor_zenith_angle,
      solar_azimuth_angle: $solar_azimuth_angle,
      solar_zenith_angle: $solar_zenith_angle
    })
    """
    params = {
        "measurement_id": measurement.measurement_id,
        "region": measurement.region,
        "timestamp": measurement.timestamp,
        "dataset": measurement.dataset,
        "CO_column_number_density": measurement.CO_column_number_density,
        "H2O_column_number_density": measurement.H2O_column_number_density,
        "cloud_height": measurement.cloud_height,
        "sensor_altitude": measurement.sensor_altitude,
        "sensor_azimuth_angle": measurement.sensor_azimuth_angle,
        "sensor_zenith_angle": measurement.sensor_zenith_angle,
        "solar_azimuth_angle": measurement.solar_azimuth_angle,
        "solar_zenith_angle": measurement.solar_zenith_angle
    }
    conn.query(query, parameters=params)

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

def create_relationships(conn: Neo4jConnection):
    # 1. Link each Measurement to its Dataset.
    query1 = """
    MATCH (m:Measurement)
    WHERE m.dataset CONTAINS 'Sentinel-5P NRTI CO'
    MATCH (d:Dataset {dataset_id: 'COPERNICUS/S5P/NRTI/L3_CO'})
    CREATE (m)-[:BELONGS_TO]->(d)
    """
    conn.query(query1)

    # 2. Link each District to its Measurements.
    query2 = """
    MATCH (d:District), (m:Measurement)
    WHERE d.name = m.region
    CREATE (d)-[:HAS_MEASUREMENT]->(m)
    """
    conn.query(query2)

def create_neighbour_relationships_from_json(conn: Neo4jConnection, json_file_path: str):
    """
    Reads the JSON file that contains districts and their neighbours,
    then creates a NEIGHBOR_OF relationship for each mapping.
    """
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
    # Connect to Neo4j
    conn = Neo4jConnection()

    # Create the Dataset node (hardcoded for this dataset)
    # dataset = Dataset(
    #     dataset_id="COPERNICUS/S5P/NRTI/L3_CO",
    #     name="Sentinel-5P NRTI CO: Near Real-Time Carbon Monoxide",
    #     description=(
    #         "This dataset provides near real-time high-resolution imagery of CO concentrations. "
    #         "Carbon monoxide (CO) is an important atmospheric trace gas for understanding tropospheric chemistry. "
    #         "In certain urban areas, it is a major atmospheric pollutant. Main sources of CO are combustion of fossil fuels, "
    #         "biomass burning, and atmospheric oxidation of methane and other hydrocarbons. Whereas fossil fuel combustion is the "
    #         "main source of CO at northern mid-latitudes, the oxidation of isoprene and biomass burning play an important role in the tropics. "
    #         "TROPOMI on the Sentinel 5 Precursor (S5P) satellite observes the CO global abundance exploiting clear-sky and cloudy-sky Earth "
    #         "radiance measurements in the 2.3 μm spectral range of the shortwave infrared (SWIR) part of the solar spectrum. "
    #         "TROPOMI clear sky observations provide CO total columns with sensitivity to the tropospheric boundary layer. "
    #         "For cloudy atmospheres, the column sensitivity changes according to the light path."
    #     ),
    #     temporal_coverage="2018-11-22T12:00:13Z–2025-02-25T08:56:13Z",
    #     spatial_resolution="1113.2 meters"
    # )
    # create_dataset_node(conn, dataset)

    # Load CSV data and create nodes
    # measurements = load_measurements("../measurements/datasets/co_measurements.csv")
    # for measurement in measurements:
    #     create_measurement_node(conn, measurement)

    # districts = load_districts("../boundaries/datasets/maharashtra_districts_details.csv")
    # for district in districts:
    #     create_district_node(conn, district)

    # Create relationships between nodes (except neighbours)
    # create_relationships(conn)

    # Create NEIGHBOR_OF relationships from JSON file
    create_neighbour_relationships_from_json(conn, "../boundaries/datasets/district_neighbours.json")

    # Close the connection
    conn.close()

if __name__ == "__main__":
    main()
