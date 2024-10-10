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

def plot_coordinates_on_terminal(screen, df, lat_col, lon_col, additional_cols=None, margin_x_percent=5, margin_y_percent=5):
    """
    Function to plot GPS coordinates on a terminal ASCII map using `asciimatics`.
    It also plots additional columns from the DataFrame next to each "X" marker, separated by "/".
    
    :param screen: asciimatics screen
    :param df: DataFrame with latitude and longitude data
    :param lat_col: Column name for latitude
    :param lon_col: Column name for longitude
    :param additional_cols: List of additional column names to display next to the "X"
    :param margin_x_percent: Horizontal margin as a percentage of the screen width
    :param margin_y_percent: Vertical margin as a percentage of the screen height
    """
    screen.clear()

    # Get screen dimensions
    max_width, max_height = screen.width, screen.height

    # Adjusting scaling based on the minimum and maximum latitude and longitude in the DataFrame
    min_lat, max_lat = df[lat_col].min(), df[lat_col].max()
    min_lon, max_lon = df[lon_col].min(), df[lon_col].max()

    # Calculate the number of characters for the margins
    margin_x = int(max_width * margin_x_percent / 100)
    margin_y = int(max_height * margin_y_percent / 100)

    # Adjust max width and height based on margins
    plot_width = max_width - 2 * margin_x
    plot_height = max_height - 2 * margin_y

    def lat_lon_to_scaled_map(lat, lon):
        """
        Converts latitude and longitude to x and y coordinates on a scaled ASCII map.
        :param lat: Latitude (from min_lat to max_lat)
        :param lon: Longitude (from min_lon to max_lon)
        :return: Scaled x, y coordinates on the map
        """
        # Scaling latitude and longitude to fit the screen (within the margin)
        x = margin_x + int((lon - min_lon) / (max_lon - min_lon) * (plot_width - 1))  # Scaled longitude
        y = margin_y + int((max_lat - lat) / (max_lat - min_lat) * (plot_height - 1))  # Scaled latitude
        return x, y

    # Loop through DataFrame rows and plot each point
    for index, row in df.iterrows():
        lat = row[lat_col]
        lon = row[lon_col]
        
        # Convert lat/lon to scaled map coordinates
        x, y = lat_lon_to_scaled_map(lat, lon)
        
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
    screen.refresh()
    screen.wait_for_input(5000)
    

def display_map(df, lat_col, lon_col, additional_cols=None, margin_x_percent=10, margin_y_percent=5):
    """
    Function to display a world map with GPS coordinates in the terminal.
    Also plots values from additional columns of the DataFrame next to the markers.
    
    :param df: DataFrame with latitude and longitude data
    :param lat_col: Column name for latitude
    :param lon_col: Column name for longitude
    :param additional_cols: List of additional column names to display next to the "X"
    :param margin_x_percent: Horizontal margin as a percentage of the screen width
    :param margin_y_percent: Vertical margin as a percentage of the screen height
    """
    Screen.wrapper(plot_coordinates_on_terminal, arguments=[df, lat_col, lon_col, additional_cols, margin_x_percent, margin_y_percent])

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
display_map(df, 'latitude', 'longitude', additional_cols=['city', 'population'], margin_x_percent=10, margin_y_percent=10)
'''