import requests
import pandas as pd
import matplotlib.pyplot as plt

def main():
    # --- 1. RETRIEVE DATA PROGRAMMATICALLY (Modern OGC API) ---
    url = "https://api.waterdata.usgs.gov/ogcapi/v0/collections/continuous/items?f=json&limit=5000&monitoring_location_id=USGS-08330000&parameter_code=00060&time=P30D"

    print(f"Connecting to MODERN USGS API...")
    response = requests.get(url)
    if response.status_code != 200:
        print("Error: Could not fetch data from modern API.")
        return
    
    json_data = response.json()

    # --- 2. LOAD AND CLEAN THE DATA ---
    try:
        features = json_data.get('features', [])
        if not features:
            print("No data found.")
            return

        # Flatten the GeoJSON structure
        df = pd.json_normalize(features)

        # CLEANING: Column Selection
        df = df[['properties.time', 'properties.value']]
        df.columns = ['timestamp', 'discharge_cfs']

        # CLEANING: Datetime parsing
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # CLEANING: Numeric conversion
        df['discharge_cfs'] = pd.to_numeric(df['discharge_cfs'], errors='coerce')
        df = df.dropna(subset=['discharge_cfs'])

        # --- 3. PRODUCE A SIMPLE SUMMARY ---
        print("\n--- MODERN API DATA SUMMARY ---")
        print(f"Observations retrieved: {len(df)}")
        print(f"Average Flow: {df['discharge_cfs'].mean():.2f} cfs")
        print(f"Max Flow:     {df['discharge_cfs'].max()} cfs")
        
        # Latest reading (Modern API sorts newest-first, so index 0)
        latest = df.iloc[0]
        print(f"Most Recent:  {latest['discharge_cfs']} cfs at {latest['timestamp']}")

        # --- 3.4 ADDING THE PLOT (OPTIONAL REQUIREMENT) ---
        # We sort by timestamp so the graph flows from left (old) to right (new)
        df_sorted = df.sort_values('timestamp')

        plt.figure(figsize=(12, 6))
        plt.plot(df_sorted['timestamp'], df_sorted['discharge_cfs'], color='#0077b6', linewidth=1.5)
        
        # Formatting the chart
        plt.title('Rio Grande Discharge at Albuquerque (Last 30 Days)', fontsize=14)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Flow (Cubic Feet per Second)', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        # Save the plot as a PNG file
        plt.savefig('water_discharge_plot.png')
        print("\n[Plot saved as 'water_discharge_plot.png']")

        # --- 4. SAVE OUTPUT ---
        df.to_csv("modern_cleaned_water_data.csv", index=False)
        print("Success: Saved to 'modern_cleaned_water_data.csv'")

    except Exception as e:
        print(f"Error parsing modern GeoJSON: {e}")

if __name__ == "__main__":
    main()