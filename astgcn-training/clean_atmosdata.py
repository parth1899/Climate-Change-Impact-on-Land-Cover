import pandas as pd

def clean_dataset(input_csv, output_csv):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(input_csv)
    
    # Optional: Replace empty strings with NaN in case missing values are recorded as blanks
    df.replace(r'^\s*$', pd.NA, regex=True, inplace=True)
    
    # Drop rows where BOTH 'ozone' and 'aerosol' values are missing.
    # This uses "how='all'" meaning that if both columns are NaN, the row is dropped.
    df_cleaned = df.dropna(subset=['ozone', 'aerosol'], how='all')
    
    # --- Alternative ---
    # If you need to drop rows when EITHER ozone or aerosol is missing, use:
    # df_cleaned = df.dropna(subset=['ozone', 'aerosol'], how='any')
    
    # Save the cleaned DataFrame to a new CSV file
    df_cleaned.to_csv(output_csv, index=False)
    print(f"Cleaned dataset saved as '{output_csv}'")

if __name__ == "__main__":
    input_csv = "cleaned_district_measurements.csv"
    output_csv = "atmos_district_measurements.csv"
    clean_dataset(input_csv, output_csv)
