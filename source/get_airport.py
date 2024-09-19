import requests
import pandas as pd
import re
from datetime import datetime

def fetch_metar_decoded(airport_code):
    # Build URL
    url = f"https://tgftp.nws.noaa.gov/data/observations/metar/decoded/{airport_code.upper()}.TXT"
    # Fetch data
    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError(f"Unable to fetch data for airport code {airport_code}")
    data = response.text
    
    # Parse data
    lines = data.strip().split('\n')
    
    # Initialize dictionary to store the data
    metar_data = {}
    
    # Loop through the lines and parse the data
    for line in lines:
        # Remove leading and trailing whitespaces
        line = line.strip()
        # Skip empty lines
        if not line:
            continue
        
        if re.match(r'.*\(.*\) \d{2}-\d{2}[NS] \d{3}-\d{2}[EW] \d+M', line):
            # Location line
            # Example: JYVASKYLA AIRPORT, Finland (EFJY) 62-24N 025-40E 141M
            metar_data['location'] = line
        elif re.match(r'\d{2}/\d{2}/\d{4} \d{2}:\d{2} UTC', line):
            # Date and time line
            # Example: 28/10/2023 08:50 UTC
            date_str = line.strip(' UTC')
            dt = datetime.strptime(date_str, '%d/%m/%Y %H:%M')
            # Convert to ISO 8601 format
            metar_data['datetime'] = dt.isoformat() + 'Z'  # Assuming UTC time
        elif line.startswith('Wind:'):
            # Wind line
            # Example: Wind: from the NNE (030 degrees) at 9 MPH (8 KT) (direction variable):0
            # Extract wind direction and speed
            # Wind: from the NNE (030 degrees) at 9 MPH (8 KT) (direction variable):0
            # Note that wind speed is given in MPH and KT
            # We'll extract the speed in KT and convert to m/s (SI units)
            # Also, we can get the direction in degrees
            wind_line = line
            # Extract direction in degrees
            match_dir = re.search(r'\((\d{3}) degrees\)', wind_line)
            if match_dir:
                metar_data['wind_direction_deg'] = int(match_dir.group(1))
            # Extract speed in KT
            match_speed = re.search(r'at (\d+) MPH \((\d+) KT\)', wind_line)
            if match_speed:
                speed_kt = int(match_speed.group(2))
                # Convert to m/s
                speed_ms = speed_kt * 0.514444
                metar_data['wind_speed_ms'] = speed_ms
            # Note: if direction is variable, handle accordingly
        elif line.startswith('Visibility:'):
            # Visibility line
            # Example: Visibility: 2 miles (3 km)
            # Extract km
            match_vis = re.search(r'Visibility:.*\(([\d\.]+) km\)', line)
            if match_vis:
                metar_data['visibility_km'] = float(match_vis.group(1))
        elif line.startswith('Sky conditions:'):
            # Sky conditions line
            # Example: Sky conditions: overcast
            metar_data['sky_conditions'] = line[len('Sky conditions:'):].strip()
        elif line.startswith('Weather:'):
            # Weather line
            # Example: Weather: light snow
            metar_data['weather'] = line[len('Weather:'):].strip()
        elif line.startswith('Temperature:'):
            # Temperature line
            # Example: Temperature: 32 F (0 C)
            match_temp = re.search(r'Temperature:.*\(([-\d\.]+) C\)', line)
            if match_temp:
                metar_data['temperature_C'] = float(match_temp.group(1))
        elif line.startswith('Dew Point:'):
            # Dew Point line
            # Example: Dew Point: 30 F (-1 C)
            match_dew = re.search(r'Dew Point:.*\(([-\d\.]+) C\)', line)
            if match_dew:
                metar_data['dew_point_C'] = float(match_dew.group(1))
        elif line.startswith('Relative Humidity:'):
            # Relative Humidity line
            # Example: Relative Humidity: 93%
            match_rh = re.search(r'Relative Humidity: (\d+)%', line)
            if match_rh:
                metar_data['relative_humidity'] = int(match_rh.group(1))
        elif line.startswith('Pressure (altimeter):'):
            # Pressure line
            # Example: Pressure (altimeter): 29.53 in. Hg (1000 hPa)
            match_press = re.search(r'Pressure \(altimeter\): .* \(([\d\.]+) hPa\)', line)
            if match_press:
                metar_data['pressure_hPa'] = float(match_press.group(1))
        elif line.startswith('ob:'):
            # Observation line
            # Ignore or store as needed
            metar_data['observation'] = line[len('ob:'):].strip()
        elif line.startswith('cycle:'):
            # Cycle line
            # Ignore or store as needed
            metar_data['cycle'] = int(line[len('cycle:'):].strip())
    
    # Now, create DataFrame
    df = pd.DataFrame([metar_data])
    
    return df
