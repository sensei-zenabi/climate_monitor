from asciimatics.screen import Screen
import pandas as pd
import time

def lat_lon_to_map(lat, lon, map_width=80, map_height=25):
    """
    Converts latitude and longitude to x and y coordinates on an ASCII map.
    :param lat: Latitude (from -90 to 90)
    :param lon: Longitude (from -180 to 180)
    :param map_width: Width of the ASCII map
    :param map_height: Height of the ASCII map
    :return: x, y coordinates on the map
    """
    # Normalize latitude and longitude to map dimensions
    x = int((lon + 180) * (map_width / 360))  # Convert lon from [-180, 180] to [0, map_width]
    y = int((90 - lat) * (map_height / 180))  # Convert lat from [-90, 90] to [0, map_height]
    return x, y

def plot_coordinates_on_terminal(screen, df, lat_col, lon_col, additional_cols=None):
    """
    Function to plot GPS coordinates on a terminal ASCII map using `asciimatics`.
    It also plots additional columns from the DataFrame next to each "X" marker, separated by "/".
    
    :param screen: asciimatics screen
    :param df: DataFrame with latitude and longitude data
    :param lat_col: Column name for latitude
    :param lon_col: Column name for longitude
    :param additional_cols: List of additional column names to display next to the "X"
    """
    screen.clear()

    # Get screen dimensions
    max_width, max_height = screen.width, screen.height

    # Loop through DataFrame rows and plot each point
    for index, row in df.iterrows():
        lat = row[lat_col]
        lon = row[lon_col]
        
        # Convert lat/lon to map coordinates
        x, y = lat_lon_to_map(lat, lon, max_width, max_height)
        
        # Prepare additional information to display
        additional_info = ""
        if additional_cols:
            additional_info = ", ".join([str(row[col]) for col in additional_cols])
        
        # Plot the point (mark it with "X") and display additional information
        if 0 <= x < max_width and 0 <= y < max_height:
            screen.print_at("X", x, y)
            if additional_info:
                screen.print_at(f" {additional_info}", x + 1, y)
    
    # Refresh the screen to update the display
    screen.refresh();
    screen.wait_for_input(5000)
    

def display_map(df, lat_col, lon_col, additional_cols=None):
    """
    Function to display a world map with GPS coordinates in the terminal.
    Also plots values from additional columns of the DataFrame next to the markers.
    
    :param df: DataFrame with latitude and longitude data3
    :param lat_col: Column name for latitude
    :param lon_col: Column name for longitude
    :param additional_cols: List of additional column names to display next to the "X"
    """
    Screen.wrapper(plot_coordinates_on_terminal, arguments=[df, lat_col, lon_col, additional_cols])

'''
# Example DataFrame with GPS coordinates and additional data
data = {
    'latitude': [51.5074, 40.7128, -33.8688, 35.6895, -23.5505],  # London, New York, Sydney, Tokyo, São Paulo
    'longitude': [-0.1278, -74.0060, 151.2093, 139.6917, -46.6333],
    'city': ['London', 'New York', 'Sydney', 'Tokyo', 'São Paulo'],
    'population': [8982000, 8419600, 5230330, 13929286, 12325232]
}
df = pd.DataFrame(data)

# Run the map display function with the example data and additional columns separated by "/"
display_map(df, 'latitude', 'longitude', additional_cols=['city', 'population'])
'''