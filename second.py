import requests
import pandas as pd
import json
import matplotlib.pyplot as plt # Added for plotting

def main():
    # --- 1. RETRIEVE DATA PROGRAMMATICALLY ---
    url = (
        "https://api.waterdata.usgs.gov/ogcapi/v0/collections/continuous/items"
        "?f=json&monitoring_location_id=USGS-08330000&parameter_code=00060&time=P30D&limit=5000"
    )

    print("Connecting to USGS API...")
    response = requests.get(url)
    response.raise_for_status()
    json_data = response.json()

    # --- SAVE RAW DATA ---
    with open("raw_data.json", "w") as f:
        json.dump(json_data, f, indent=4)
    print("Success: Raw data saved to 'raw_data.json'")

    # --- 2. LOAD AND CLEAN THE DATA ---
    features = json_data.get("features", [])
    df = pd.json_normalize(features)

    # CHECK FOR NULL VALUES
    initial_nulls = df['properties.value'].isna().sum()
    print(f"Checking for null values: Found {initial_nulls} missing entries.")

    # CLEANING: Column Selection and Datetime Parsing
    df = df[['properties.time', 'properties.value']]
    df.columns = ['timestamp', 'discharge_cfs']
    
    # Convert to local Mountain Time (Website time)
    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_convert('US/Mountain')
    
    # Create AM/PM format for the CSV
    df['time_ampm'] = df['timestamp'].dt.strftime('%Y-%m-%d %I:%M %p')

    # CLEANING: Numeric conversion and drop nulls
    df['discharge_cfs'] = pd.to_numeric(df['discharge_cfs'], errors='coerce')
    df = df.dropna(subset=['discharge_cfs'])

    # --- 3. PRODUCE A SIMPLE SUMMARY ---
    print("\n" + "="*30)
    print("      DATA SUMMARY")
    print("="*30)
    print(f"Total Observations: {len(df)}")
    print(f"Minimum Flow:       {df['discharge_cfs'].min()} cfs")
    print(f"Maximum Flow:       {df['discharge_cfs'].max()} cfs")
    print(f"Average Flow:       {df['discharge_cfs'].mean():.2f} cfs")
    
    latest = df.iloc[-1]
    print(f"Latest Reading:     {latest['discharge_cfs']} cfs")
    print(f"Latest Time:        {latest['time_ampm']}")
    print("="*30)

    # --- 4. GENERATE PLOT DIAGRAM ---
    print("\nGenerating plot...")
    plt.figure(figsize=(10, 6))
    plt.plot(df['timestamp'], df['discharge_cfs'], color='blue', linewidth=2)
    
    # Adding labels and title
    plt.title('Rio Grande Discharge at Albuquerque (Last 30 Days)', fontsize=14)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Discharge (cubic feet per second)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Formatting the layout
    plt.tight_layout()
    plt.savefig("water_chart.png") # Saves the plot as an image
    print("Success: Plot saved as 'water_chart.png'")

    # --- 5. SAVE CSV OUTPUT ---
    df_final = df[['time_ampm', 'discharge_cfs']]
    df_final.to_csv("cleaned_water_data.csv", index=False)
    print("Success: Cleaned dataset saved as 'cleaned_water_data.csv'")

if __name__ == "__main__":
    main()
