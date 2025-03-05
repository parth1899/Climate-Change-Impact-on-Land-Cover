import csv
from neo4j_connection import Neo4jConnection
from models import Dataset, Ozone_Measurement  

def safe_float(value, default=None):
    """
    Safely convert a string value to float.
    Returns default if value is empty or invalid.
    """
    try:
        return float(value) if value != "" else default
    except ValueError:
        return default

def load_ozone_measurements(file_path: str, missing_file: str = "missing_ozone_records.csv"):
    """
    Loads ozone measurement data from a CSV file into Ozone_Measurement objects.
    Any rows missing required numeric fields are logged into a separate CSV file.
    """
    measurements = []
    missing_records = []
    numeric_fields = [
        "O3_column_number_density",
        "O3_column_number_density_amf",
        "O3_slant_column_number_density",
        "O3_effective_temperature",
        "cloud_fraction",
        "sensor_azimuth_angle",
        "sensor_zenith_angle",
        "solar_azimuth_angle",
        "solar_zenith_angle"
    ]
    
    with open(file_path, "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row_number, row in enumerate(reader, start=1):
            # Check for missing numeric values.
            if any(row.get(field, "").strip() == "" for field in numeric_fields):
                missing_record = {"row_number": row_number}
                missing_record.update(row)
                missing_records.append(missing_record)
                continue

            measurements.append(
                Ozone_Measurement(
                    measurement_id=row["measurement_id"],
                    region=row["district_name"],
                    timestamp=row["timestamp"],
                    dataset=row["dataset"],
                    O3_column_number_density=safe_float(row["O3_column_number_density"]),
                    O3_column_number_density_amf=safe_float(row["O3_column_number_density_amf"]),
                    O3_slant_column_number_density=safe_float(row["O3_slant_column_number_density"]),
                    O3_effective_temperature=safe_float(row["O3_effective_temperature"]),
                    cloud_fraction=safe_float(row["cloud_fraction"]),
                    sensor_azimuth_angle=safe_float(row["sensor_azimuth_angle"]),
                    sensor_zenith_angle=safe_float(row["sensor_zenith_angle"]),
                    solar_azimuth_angle=safe_float(row["solar_azimuth_angle"]),
                    solar_zenith_angle=safe_float(row["solar_zenith_angle"])
                )
            )
    
    if missing_records:
        with open(missing_file, "w", encoding="utf-8", newline="") as missing_csvfile:
            fieldnames = list(missing_records[0].keys())
            writer = csv.DictWriter(missing_csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(missing_records)
        print(f"Missing records written to {missing_file}")
    
    return measurements

def create_dataset_node(conn: Neo4jConnection, dataset: Dataset):
    """
    Creates (or merges) a Dataset node. Using MERGE ensures that if the dataset node already exists,
    it won’t be duplicated.
    """
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

def create_ozone_measurement_node(conn: Neo4jConnection, measurement: Ozone_Measurement):
    """
    Creates (or merges) an Ozone_Measurement node. Using MERGE prevents duplicate nodes
    if the script is run multiple times.
    """
    query = """
    MERGE (m:Ozone_Measurement {measurement_id: $measurement_id})
    SET m.region = $region,
        m.timestamp = $timestamp,
        m.dataset = $dataset,
        m.O3_column_number_density = $O3_column_number_density,
        m.O3_column_number_density_amf = $O3_column_number_density_amf,
        m.O3_slant_column_number_density = $O3_slant_column_number_density,
        m.O3_effective_temperature = $O3_effective_temperature,
        m.cloud_fraction = $cloud_fraction,
        m.sensor_azimuth_angle = $sensor_azimuth_angle,
        m.sensor_zenith_angle = $sensor_zenith_angle,
        m.solar_azimuth_angle = $solar_azimuth_angle,
        m.solar_zenith_angle = $solar_zenith_angle
    """
    params = {
        "measurement_id": measurement.measurement_id,
        "region": measurement.region,
        "timestamp": measurement.timestamp,
        "dataset": measurement.dataset,
        "O3_column_number_density": measurement.O3_column_number_density,
        "O3_column_number_density_amf": measurement.O3_column_number_density_amf,
        "O3_slant_column_number_density": measurement.O3_slant_column_number_density,
        "O3_effective_temperature": measurement.O3_effective_temperature,
        "cloud_fraction": measurement.cloud_fraction,
        "sensor_azimuth_angle": measurement.sensor_azimuth_angle,
        "sensor_zenith_angle": measurement.sensor_zenith_angle,
        "solar_azimuth_angle": measurement.solar_azimuth_angle,
        "solar_zenith_angle": measurement.solar_zenith_angle
    }
    conn.query(query, parameters=params)

def create_ozone_relationships(conn: Neo4jConnection):
    """
    Creates relationships for the Ozone_Measurement nodes. These include:
      1. Linking each Ozone_Measurement to its Dataset node.
      2. Linking each District (already present) to its Ozone_Measurement.
    MERGE is used to ensure that running this script multiple times will not create duplicate relationships.
    """
    # Link each Ozone_Measurement to its Dataset.
    query1 = """
    MATCH (m:Ozone_Measurement)
    WHERE m.dataset CONTAINS "Sentinel-5P NRTI O3"
    MATCH (d:Dataset {dataset_id: 'COPERNICUS/S5P/NRTI/L3_O3'})
    MERGE (m)-[:BELONGS_TO]->(d)
    """
    conn.query(query1)

    # Link each District to its Ozone_Measurement.
    query2 = """
    MATCH (d:District), (m:Ozone_Measurement)
    WHERE d.name = m.region
    MERGE (d)-[:HAS_MEASUREMENT]->(m)
    """
    conn.query(query2)

def main():
    # Connect to Neo4j.
    conn = Neo4jConnection()

    # Optionally create the Dataset node for Ozone measurements if it does not already exist.
    # ozone_dataset = Dataset(
    #     dataset_id="COPERNICUS/S5P/NRTI/L3_O3",
    #     name="Sentinel-5P NRTI O3: Near Real-Time Ozone",
    #     description=("This dataset provides near-real-time high-resolution imagery of total column ozone concentrations. See also COPERNICUS/S5P/OFFL/L3_O3_TCL for the tropospheric column data. In the stratosphere, the ozone layer shields the biosphere from dangerous solar ultraviolet radiation. In the troposphere, it acts as an efficient cleansing agent, but at high concentration it also becomes harmful to the health of humans, animals, and vegetation. Ozone is also an important greenhouse-gas contributor to ongoing climate change. Since the discovery of the Antarctic ozone hole in the 1980s and the subsequent Montreal Protocol regulating the production of chlorine-containing ozone-depleting substances, ozone has been routinely monitored from the ground and from space. For this product, there are two algorithms that deliver total ozone: GDP for the near real-time and GODFIT for the offline products. GDP is currently being used for generating the operational total ozone products from GOME, SCIAMACHY and GOME-2; while GODFIT is being used in the ESA CCI and the Copernicus C3S projects."),
    #     temporal_coverage="2018-07-10T11:02:44Z–2025-02-26T10:16:13Z",
    #     spatial_resolution="1113.2 meters"
    # )
    # create_dataset_node(conn, ozone_dataset)

    # Load ozone measurements from the CSV file.
    measurements = load_ozone_measurements("../measurements/datasets/o3_measurements.csv")
    for measurement in measurements:
        create_ozone_measurement_node(conn, measurement)

    # Create relationships between the new Ozone_Measurement nodes and existing Dataset and District nodes.
    create_ozone_relationships(conn)

    # Close the connection.
    conn.close()

if __name__ == "__main__":
    main()
