import requests
import pandas as pd
import matplotlib.pyplot as plt

def main():
    # --- 1. RETRIEVE DATA PROGRAMMATICALLY ---
    # Fetching data for: One site, One parameter (Discharge), 30-day period
    site_id = "08330000"  # Rio Grande at Albuquerque, NM
    parameter_code = "00060"  # Discharge (cubic feet per second)
    period = "P30D" # Last 30 days
    
    url = f"https://nwis.waterservices.usgs.gov/nwis/iv/?format=json&sites={site_id}&parameterCd={parameter_code}&period={period}"

    print(f"Connecting to USGS API for site {site_id}...")
    response = requests.get(url)
    
    if response.status_code != 200:
        print("Failed to retrieve data.")
        return

    json_data = response.json()

    # --- 2. LOAD AND CLEAN THE DATA ---
    try:
        # Navigate the nested JSON structure
        raw_values = json_data['value']['timeSeries'][0]['values'][0]['value']
        
        # Load into Pandas
        df = pd.DataFrame(raw_values)

        # CLEANING: Datetime parsing
        df['dateTime'] = pd.to_datetime(df['dateTime'])
        
        # CLEANING: Convert values to numeric (handling errors)
        df['value'] = pd.to_numeric(df['value'], errors='coerce')

        # CLEANING: Missing values (Requirement 2.2.1)
        df = df.dropna(subset=['value'])

        # CLEANING: Column selection (Requirement 2.2.2)
        df = df.rename(columns={'dateTime': 'timestamp', 'value': 'discharge_cfs'})
        df = df[['timestamp', 'discharge_cfs']]

        # --- 3. PRODUCE A SIMPLE SUMMARY ---
        print("\n--- DATA SUMMARY ---")
        # Number of observations retrieved
        print(f"Total Observations: {len(df)}")
        
        # Min / max / average value
        print(f"Minimum Flow: {df['discharge_cfs'].min()} cfs")
        print(f"Maximum Flow: {df['discharge_cfs'].max()} cfs")
        print(f"Average Flow: {df['discharge_cfs'].mean():.2f} cfs")
        
        # Most recent measurement
        latest_val = df.iloc[-1]['discharge_cfs']
        latest_time = df.iloc[-1]['timestamp']
        print(f"Most Recent: {latest_val} cfs at {latest_time}")

        # Simple plot (Optional but recommended)
        plt.figure(figsize=(10, 5))
        plt.plot(df['timestamp'], df['discharge_cfs'], color='blue')
        plt.title('Rio Grande Discharge (Last 30 Days)')
        plt.xlabel('Date')
        plt.ylabel('Flow (cfs)')
        plt.grid(True)
        plt.savefig('water_summary_plot.png')
        print("\n[Plot saved as water_summary_plot.png]")

        # --- 4. SAVE OUTPUT ---
        # Save the cleaned dataset as a CSV
        df.to_csv("cleaned_water_data.csv", index=False)
        print("Success: Cleaned data saved to 'cleaned_water_data.csv'")

    except (KeyError, IndexError) as e:
        print(f"Data Error: The API returned an empty or unexpected format. {e}")

if __name__ == "__main__":
    main()