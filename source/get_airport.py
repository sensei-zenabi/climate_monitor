import requests
import pandas as pd
import re
from datetime import datetime

URL_AIRPORTS_ROOT = "https://tgftp.nws.noaa.gov/data/observations/metar/decoded/"

def get_data(airport_code):
    # URL to fetch METAR decoded data from NOAA
    url = f"https://tgftp.nws.noaa.gov/data/observations/metar/decoded/{airport_code}.TXT"
    
    # Fetch the METAR data
    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError(f"Could not fetch data for airport code {airport_code}. Please check the code and try again.")
    
    # Get the raw text data
    data = response.text
    
    # Initialize dictionary for storing extracted data
    raw_data = {
        'location': None,
        'latitude_dms': None,
        'longitude_dms': None,
        'timestamp_utc': None,
        'wind_speed_knots': None,
        'visibility_miles': None,
        'temperature_C': None,
        'dew_point_C': None,
        'humidity_percent': None,
        'pressure_hPa': None
    }

    # Extract relevant fields from the METAR text
    raw_data['location'] = re.search(r'^(.*) \(\w+\)', data).group(1)  # Location
    raw_data['latitude_dms'], raw_data['longitude_dms'] = re.search(r'(\d+-\d+\w) (\d+-\d+\w)', data).groups()  # Latitude, Longitude
    raw_data['timestamp_utc'] = re.search(r'(\d{4}\.\d{2}\.\d{2} \d{4} UTC)', data).group(1)  # Timestamp in UTC
    
    # Extract wind speed in knots
    wind_match = re.search(r'Wind: .* at (\d+) MPH \((\d+) KT\)', data)
    if wind_match:
        raw_data['wind_speed_knots'] = int(wind_match.group(2))  # Wind speed in knots
    
    # Extract visibility in miles
    visibility_match = re.search(r'Visibility: (greater than )?(\d+) mile', data)
    if visibility_match:
        raw_data['visibility_miles'] = int(visibility_match.group(2))
    
    # Extract temperature and dew point in Celsius
    temp_match = re.search(r'Temperature:.*\(([\d\.]+) C\)', data)
    dew_point_match = re.search(r'Dew Point:.*\(([\d\.]+) C\)', data)
    if temp_match:
        raw_data['temperature_C'] = float(temp_match.group(1))  # Allowing decimal temperatures
    if dew_point_match:
        raw_data['dew_point_C'] = float(dew_point_match.group(1))  # Allowing decimal dew points

    # Extract humidity and pressure
    humidity_match = re.search(r'Relative Humidity: (\d+)%', data)
    pressure_match = re.search(r'Pressure \(altimeter\):.*\((\d+) hPa\)', data)
    if humidity_match:
        raw_data['humidity_percent'] = int(humidity_match.group(1))
    if pressure_match:
        raw_data['pressure_hPa'] = int(pressure_match.group(1))
    
    # Convert timestamp to ISO 8601 format
    timestamp = datetime.strptime(raw_data['timestamp_utc'], "%Y.%m.%d %H%M %Z")
    timestamp_iso = timestamp.isoformat()

    # Convert latitude and longitude from DMS to decimal
    def dms_to_decimal(dms_str):
        match = re.match(r'(\d+)-(\d+)([NSEW])', dms_str)
        degrees = int(match.group(1))
        minutes = int(match.group(2)) / 60
        direction = match.group(3)
        decimal = degrees + minutes
        if direction in ['S', 'W']:
            decimal = -decimal
        return decimal

    latitude = dms_to_decimal(raw_data['latitude_dms'])
    longitude = dms_to_decimal(raw_data['longitude_dms'])

    # Convert wind speed from knots to meters per second
    wind_speed_m_s = raw_data['wind_speed_knots'] * 0.514444

    # Convert visibility from miles to kilometers
    visibility_km = raw_data['visibility_miles'] * 1.60934 if raw_data['visibility_miles'] else None

    # Prepare the final data dictionary with SI units and ISO timestamp
    weather_data = {
        'timestamp': timestamp_iso,
        'location': raw_data['location'],
        'latitude': round(latitude, 4),
        'longitude': round(longitude, 4),
        'wind_speed_m_s': round(wind_speed_m_s, 2),
        'visibility_km': round(visibility_km, 2) if visibility_km else None,
        'temperature_C': raw_data['temperature_C'],
        'dew_point_C': raw_data['dew_point_C'],
        'relative_humidity': raw_data['humidity_percent'],
        'pressure_hPa': raw_data['pressure_hPa']
    }

    # Convert to pandas DataFrame
    # df = pd.DataFrame([weather_data])
    
    return weather_data

# Example usage
# df = extract_metar_data("EFJY")
# print(df)
