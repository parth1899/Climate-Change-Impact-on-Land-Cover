import csv
from neo4j_connection import Neo4jConnection
from models import Dataset, Aerosol_AI_Measurement  

def safe_float(value, default=None):
    """
    Safely convert a string value to float.
    Returns default if value is empty or invalid.
    """
    try:
        return float(value) if value != "" else default
    except ValueError:
        return default

def load_aerosol_measurements(file_path: str, missing_file: str = "missing_aerosol_records.csv"):
    """
    Loads aerosol measurement data from a CSV file into Aerosol_AI_Measurement objects.
    Any rows missing required numeric fields are logged into a separate CSV file.
    """
    measurements = []
    missing_records = []
    numeric_fields = [
        "absorbing_aerosol_index",
        "sensor_altitude",
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
                Aerosol_AI_Measurement(
                    measurement_id=row["measurement_id"],
                    region=row["district_name"],
                    timestamp=row["timestamp"],
                    dataset=row["dataset"],
                    absorbing_aerosol_index=safe_float(row["absorbing_aerosol_index"]),
                    sensor_altitude=safe_float(row["sensor_altitude"]),
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

def create_aerosol_measurement_node(conn: Neo4jConnection, measurement: Aerosol_AI_Measurement):
    """
    Creates (or merges) an Aerosol_AI_Measurement node. Using MERGE prevents duplicate nodes
    if the script is run multiple times.
    """
    query = """
    MERGE (m:Aerosol_AI_Measurement {measurement_id: $measurement_id})
    SET m.region = $region,
        m.timestamp = $timestamp,
        m.dataset = $dataset,
        m.absorbing_aerosol_index = $absorbing_aerosol_index,
        m.sensor_altitude = $sensor_altitude,
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
        "absorbing_aerosol_index": measurement.absorbing_aerosol_index,
        "sensor_altitude": measurement.sensor_altitude,
        "sensor_azimuth_angle": measurement.sensor_azimuth_angle,
        "sensor_zenith_angle": measurement.sensor_zenith_angle,
        "solar_azimuth_angle": measurement.solar_azimuth_angle,
        "solar_zenith_angle": measurement.solar_zenith_angle
    }
    conn.query(query, parameters=params)

def create_aerosol_relationships(conn: Neo4jConnection):
    """
    Creates relationships for the Aerosol_Measurement nodes. These include:
      1. Linking each Aerosol_AI_Measurement to its Dataset node.
      2. Linking each District (already present) to its Aerosol_AI_Measurement.
    MERGE is used to ensure that running this script multiple times will not create duplicate relationships.
    """
    # Link each Aerosol_AI_Measurement to its Dataset.
    query1 = """
    MATCH (m:Aerosol_AI_Measurement)
    WHERE m.dataset CONTAINS "Sentinel-5P NRTI AER AI"
    MATCH (d:Dataset {dataset_id: 'COPERNICUS/S5P/NRTI/L3_AER_AI'})
    MERGE (m)-[:BELONGS_TO]->(d)
    """
    conn.query(query1)

    # Link each District to its Aerosol_Measurement.
    query2 = """
    MATCH (d:District), (m:Aerosol_AI_Measurement)
    WHERE d.name = m.region
    MERGE (d)-[:HAS_MEASUREMENT]->(m)
    """
    conn.query(query2)

def main():
    # Connect to Neo4j.
    conn = Neo4jConnection()

    # Optionally create the Dataset node for Aerosol measurements if it does not already exist.
    aerosol_dataset = Dataset(
        dataset_id="COPERNICUS/S5P/NRTI/L3_AER_AI",
        name="Sentinel-5P NRTI AER AI: Near Real-Time UV Aerosol Index",
        description=("This dataset provides near real-time high-resolution imagery of the UV Aerosol Index (UVAI), also called the Absorbing Aerosol Index (AAI). The AAI is based on wavelength-dependent changes in Rayleigh scattering in the UV spectral range for a pair of wavelengths. The difference between observed and modelled reflectance results in the AAI. When the AAI is positive, it indicates the presence of UV-absorbing aerosols like dust and smoke. It is useful for tracking the evolution of episodic aerosol plumes from dust outbreaks, volcanic ash, and biomass burning. The wavelengths used have very low ozone absorption, so unlike aerosol optical thickness measurements, AAI can be calculated in the presence of clouds. Daily global coverage is therefore possible. For this L3 AER_AI product, the absorbing_aerosol_index is calculated with a pair of measurements at the 354 nm and 388 nm wavelengths."),
        temporal_coverage="2018-07-10T11:17:44Z–2025-02-26T10:16:13Z",
        spatial_resolution="1113.2 meters"
    )
    create_dataset_node(conn, aerosol_dataset)

    # Load Aerosol measurements from the CSV file.
    measurements = load_aerosol_measurements("../measurements/datasets/aer_ai_measurements.csv")
    for measurement in measurements:
        create_aerosol_measurement_node(conn, measurement)

    # Create relationships between the new Aerosol_Measurement nodes and existing Dataset and District nodes.
    create_aerosol_relationships(conn)

    # Close the connection.
    conn.close()

if __name__ == "__main__":
    main()
