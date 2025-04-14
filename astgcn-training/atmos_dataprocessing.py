import pandas as pd

# Read the CSV file into a DataFrame
df = pd.read_csv("district_measurements_by_date.csv")

# Convert the 'date' column to datetime
df['date'] = pd.to_datetime(df['date'])

# Create a new column for lookup: expected date for the CO measurement
df['lookup_timestamp'] = df['date'] + pd.Timedelta(days=2)

# Create a lookup DataFrame: for each district, we extract the date and its CO measurement.
# We rename 'date' to 'lookup_timestamp' so that we can merge on district and lookup_timestamp.
df_lookup = df[['district', 'date', 'co']].rename(
    columns={'date': 'lookup_timestamp', 'co': 'co_future'}
)

# Merge the original dataframe with the lookup dataframe on district and lookup_timestamp.
# This brings in the CO measurement from the row that is 2 days later.
df_merged = pd.merge(df, df_lookup, on=['district', 'lookup_timestamp'], how='left')

# For each row, if the original 'co' is missing, try to fill it with 'co_future'.
df_merged['co'] = df_merged.apply(
    lambda row: row['co'] if pd.notnull(row['co']) else row['co_future'],
    axis=1
)

# Now, drop any rows that still have missing CO values
df_cleaned = df_merged[pd.notnull(df_merged['co'])].copy()

# Optionally, drop the helper columns used for merging
df_cleaned.drop(columns=['lookup_timestamp', 'co_future'], inplace=True)

# Save the cleaned DataFrame to a new CSV file
df_cleaned.to_csv("cleaned_district_measurements.csv", index=False)

print("Cleaned CSV file saved as 'cleaned_district_measurements.csv'")
