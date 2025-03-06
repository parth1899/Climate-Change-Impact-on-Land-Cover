import csv
from neo4j_connection import Neo4jConnection
from models import Dataset, LandCoverMeasurement  # Ensure LandCoverMeasurement is defined in your models

def safe_float(value, default=None):
    """
    Safely convert a string value to float.
    Returns default if value is empty or invalid.
    """
    try:
        return float(value) if value != "" else default
    except ValueError:
        return default

def load_landcover_measurements(file_path: str, missing_file: str = "missing_landcover_records.csv"):
    """
    Loads land cover measurement data from a CSV file into LandCoverMeasurement objects.
    Any rows missing required numeric fields are logged into a separate CSV file.
    """
    measurements = []
    missing_records = []
    numeric_fields = [
        "Water", "Trees", "Flooded_Vegetation", "Crops",
        "Built_Area", "Bare_Ground", "Snow_Ice", "Clouds", "Rangeland"
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
                LandCoverMeasurement(
                    measurement_id=row["measurement_id"],
                    region=row["district_name"],
                    # Using the year as timestamp; adjust as needed (e.g., to a full ISO date)
                    timestamp=row["year"],
                    dataset=row["dataset"],
                    Water=safe_float(row["Water"]),
                    Trees=safe_float(row["Trees"]),
                    Flooded_Vegetation=safe_float(row["Flooded_Vegetation"]),
                    Crops=safe_float(row["Crops"]),
                    Built_Area=safe_float(row["Built_Area"]),
                    Bare_Ground=safe_float(row["Bare_Ground"]),
                    Snow_Ice=safe_float(row["Snow_Ice"]),
                    Clouds=safe_float(row["Clouds"]),
                    Rangeland=safe_float(row["Rangeland"])
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
    Creates (or merges) a Dataset node.
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

def create_landcover_measurement_node(conn: Neo4jConnection, measurement: LandCoverMeasurement):
    """
    Creates (or merges) a LandCoverMeasurement node.
    """
    query = """
    MERGE (m:LandCoverMeasurement {measurement_id: $measurement_id})
    SET m.region = $region,
        m.timestamp = $timestamp,
        m.dataset = $dataset,
        m.Water = $Water,
        m.Trees = $Trees,
        m.Flooded_Vegetation = $Flooded_Vegetation,
        m.Crops = $Crops,
        m.Built_Area = $Built_Area,
        m.Bare_Ground = $Bare_Ground,
        m.Snow_Ice = $Snow_Ice,
        m.Clouds = $Clouds,
        m.Rangeland = $Rangeland
    """
    params = {
        "measurement_id": measurement.measurement_id,
        "region": measurement.region,
        "timestamp": measurement.timestamp,
        "dataset": measurement.dataset,
        "Water": measurement.Water,
        "Trees": measurement.Trees,
        "Flooded_Vegetation": measurement.Flooded_Vegetation,
        "Crops": measurement.Crops,
        "Built_Area": measurement.Built_Area,
        "Bare_Ground": measurement.Bare_Ground,
        "Snow_Ice": measurement.Snow_Ice,
        "Clouds": measurement.Clouds,
        "Rangeland": measurement.Rangeland
    }
    conn.query(query, parameters=params)

def create_landcover_relationships(conn: Neo4jConnection):
    """
    Creates relationships for LandCoverMeasurement nodes.
    These include:
      1. Linking each LandCoverMeasurement to its Dataset node.
      2. Linking each District (already present) to its LandCoverMeasurement.
    """
    # Link each LandCoverMeasurement to its Dataset.
    query1 = """
    MATCH (m:LandCoverMeasurement)
    WHERE m.dataset CONTAINS "ESRI 10m Annual Land Cover"
    MATCH (d:Dataset {dataset_id: 'ESRI_Global_LULC_10m_TS'})
    MERGE (m)-[:BELONGS_TO]->(d)
    """
    conn.query(query1)
    
    # Link each District to its LandCoverMeasurement.
    query2 = """
    MATCH (d:District), (m:LandCoverMeasurement)
    WHERE d.name = m.region
    MERGE (d)-[:HAS_MEASUREMENT]->(m)
    """
    conn.query(query2)

def main():
    # Connect to Neo4j.
    conn = Neo4jConnection()

    # Create the Dataset node for ESRI Land Cover measurements.
    landcover_dataset = Dataset(
        dataset_id="ESRI_Global_LULC_10m_TS",
        name="ESRI 10m Annual Land Cover (2017-2023)",
        description=(
            "Time series of annual global maps of land use and land cover derived from "
            "ESA Sentinel-2 imagery at 10m resolution. Each map is a composite of LULC predictions "
            "for 9 classes over each year. Produced by Impact Observatory for Esri with over 75% accuracy."
        ),
        temporal_coverage="2017–2023",
        spatial_resolution="10 meters"
    )
    create_dataset_node(conn, landcover_dataset)

    # Load land cover measurements from the CSV file.
    measurements = load_landcover_measurements("../measurements/datasets/esri_lulc_measurements.csv")
    for measurement in measurements:
        create_landcover_measurement_node(conn, measurement)

    # Create relationships linking measurements to their dataset and districts.
    create_landcover_relationships(conn)

    # Close the connection.
    conn.close()

if __name__ == "__main__":
    main()
