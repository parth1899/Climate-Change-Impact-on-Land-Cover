import pandas as pd
from neo4j_connection import neo4j_connection

# Query to fetch the list of districts.
GET_DISTRICTS_QUERY = """
MATCH (d:District)
RETURN d.name AS district
ORDER BY d.name
"""

# UNION query to fetch all atmospheric measurements (CO, Ozone, Aerosol)
# For each branch, only the date part (first 10 characters) of the timestamp is returned.
UNION_QUERY = """
// CO measurements
MATCH (d:District {name: $district})-[:HAS_MEASUREMENT]->(co:CO_Measurement)
RETURN $district AS district,
       substring(co.timestamp, 0, 10) AS date,
       co.measurement_id AS id,
       co.CO_column_number_density AS value,
       "CO" AS parameter
UNION ALL
// Ozone measurements
MATCH (d:District {name: $district})-[:HAS_MEASUREMENT]->(oz:Ozone_Measurement)
RETURN $district AS district,
       substring(oz.timestamp, 0, 10) AS date,
       oz.measurement_id AS id,
       oz.O3_column_number_density AS value,
       "Ozone" AS parameter
UNION ALL
// Aerosol measurements
MATCH (d:District {name: $district})-[:HAS_MEASUREMENT]->(a:Aerosol_AI_Measurement)
RETURN $district AS district,
       substring(a.timestamp, 0, 10) AS date,
       a.measurement_id AS id,
       a.absorbing_aerosol_index AS value,
       "Aerosol" AS parameter
ORDER BY date
"""

def fetch_districts():
    """Fetches and returns a list of all district names."""
    results = neo4j_connection.execute_query(GET_DISTRICTS_QUERY)
    return [record["district"] for record in results]

def fetch_raw_measurements(district):
    """
    For a given district, executes the UNION query to fetch all atmospheric measurements.
    Returns a list of records.
    """
    results = neo4j_connection.execute_query(UNION_QUERY, {"district": district})
    return results

def main():
    districts = fetch_districts()
    all_data = []
    
    # Fetch data for each district one by one.
    for district in districts:
        print(f"Fetching data for district: {district}")
        district_data = fetch_raw_measurements(district)
        all_data.extend(district_data)
    
    # Convert the collected data into a DataFrame.
    df = pd.DataFrame(all_data)
    
    # Pivot the data so that each row corresponds to a unique (district, date) combination
    # and separate columns are created for each atmospheric measurement type.
    # The pivot table uses the "value" field and the "parameter" field to define the columns.
    df_pivot = df.pivot_table(index=["district", "date"], 
                              columns="parameter", 
                              values="value", 
                              aggfunc="first").reset_index()
    
    # Flatten the column names.
    df_pivot.columns.name = None
    df_pivot.columns = [str(col) for col in df_pivot.columns]
    
    # Optionally sort by district and date.
    df_pivot = df_pivot.sort_values(by=["district", "date"])
    
    # Write the pivoted DataFrame to a CSV file.
    output_csv = "district_measurements_by_date.csv"
    df_pivot.to_csv(output_csv, index=False)
    print(f"Pivoted data written to {output_csv}")

if __name__ == "__main__":
    main()
