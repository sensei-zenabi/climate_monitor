import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt 
import mplcursors
import warnings
import threading
import os

import get_data
import vmath

# %% Configuration

with open('config.py') as file:
    exec(file.read())

URL_BUOY_REALTIME_ROOT = "https://www.ndbc.noaa.gov/data/realtime2/"
URL_BUOY_STATION_INFO = "https://www.ndbc.noaa.gov/data/stations/station_table.txt"
URL_SPACE_ROOT = "https://services.swpc.noaa.gov/text/"

warnings.filterwarnings("default");

# %% Fetch buoy data from ndbc.noaa.gov

# Information and metadata related to buoys
DF_BUOY_IDs = get_data.get_files_from_server(URL_BUOY_REALTIME_ROOT)
DF_STATION_INFO = get_data.get_table_from_server(URL_BUOY_STATION_INFO)

# Filter the station info to contain only the buoys from which there are realtime data 
DF_STATION_INFO = DF_STATION_INFO[DF_STATION_INFO['# STATION_ID'].isin(DF_BUOY_IDs['Filename'])].reset_index().drop(['index'], axis=1);

# Fix the GPS format
DF_STATION_INFO['LOCATION'] = DF_STATION_INFO['LOCATION'].str.split('(').str[0].str.strip()
DF_STATION_INFO['LATITUDE'], DF_STATION_INFO['LONGITUDE'] = zip(*DF_STATION_INFO['LOCATION'].apply(lambda x: vmath.convert_location(x)))

# Get the columns for the realtime data using the first available station realtime data header
COLS = get_data.get_table_columns_from_server(URL_BUOY_REALTIME_ROOT, DF_STATION_INFO['# STATION_ID'][0])
COLS = COLS[0].split()

# %% APP - STATION BROWSER
# For maps: https://www.naturalearthdata.com/downloads/110m-cultural-vectors/
# For annotations: https://mplcursors.readthedocs.io/en/stable/examples/change_popup_color.html

# Thread: GUI World Map
def map_thread():

    # Path to the downloaded shapefile
    shapefile_path = 'ne_10m_admin_0_countries.shp'

    # Load the world map from the shapefile
    world = gpd.read_file(shapefile_path)

    # Convert the DataFrame to a GeoDataFrame
    gdf = gpd.GeoDataFrame(
        DF_STATION_INFO, 
        geometry=gpd.points_from_xy(DF_STATION_INFO['LONGITUDE'], DF_STATION_INFO['LATITUDE']))
    
    # Plot the world map
    plt.rcParams['toolbar'] = 'None' # 'toolbar2' to get back on
    fig = plt.figure(facecolor='black', figsize=(16,9))
    ax = fig.add_subplot()
    ax.set_facecolor('black')
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    world.plot(ax=ax, color='forestgreen', edgecolor='limegreen', alpha=0.5, lw=0.5)
    plt.title('ACTIVE MEASUREMENT STATIONS', color='limegreen', fontname='Ubuntu', fontsize=16)
    plt.text(-190,-106,s="Click station to view details", color='limegreen', fontsize=10)
    plt.text(-190,-110,s="Press Q to Exit plot", color='limegreen', fontsize=10)
    manager = plt.get_current_fig_manager()
    manager.full_screen_toggle()

    # Plot the GPS coordinates
    sc = gdf.plot(ax=plt.gca(), 
                  c=pd.to_numeric(gdf['# STATION_ID']) / pd.to_numeric(gdf['# STATION_ID']).max(), 
                  markersize=25)

    # Use mplcursors to annotate the points with the Station ID on mouse click
    cursor = mplcursors.cursor(sc, hover=False)
    
    @cursor.connect("add")
    def on_add(sel):
        station_id = DF_STATION_INFO.iloc[sel.index]['# STATION_ID']
        ttype = DF_STATION_INFO.iloc[sel.index]['TTYPE']
        location = DF_STATION_INFO.iloc[sel.index]['LOCATION']
        wtrtemp = get_data.get_table_latest_value_from_server(URL_BUOY_REALTIME_ROOT, 
                                                              station_id,
                                                              COLS[14])
        airtemp = get_data.get_table_latest_value_from_server(URL_BUOY_REALTIME_ROOT, 
                                                              station_id,
                                                              COLS[13])
        yy = get_data.get_table_latest_value_from_server(URL_BUOY_REALTIME_ROOT, 
                                                         station_id,
                                                         COLS[0])
        mm = get_data.get_table_latest_value_from_server(URL_BUOY_REALTIME_ROOT, 
                                                         station_id,
                                                         COLS[1])
        dd = get_data.get_table_latest_value_from_server(URL_BUOY_REALTIME_ROOT, 
                                                         station_id,
                                                         COLS[2])
        hh = get_data.get_table_latest_value_from_server(URL_BUOY_REALTIME_ROOT, 
                                                         station_id,
                                                         COLS[2])
        mn = get_data.get_table_latest_value_from_server(URL_BUOY_REALTIME_ROOT, 
                                                         station_id,
                                                         COLS[3])
        sel.annotation.set(text=f"ID: {station_id} - {ttype}\nLocation: {location}\nLast Confirmed Time: {yy}-{mm}-{dd} {hh}:{mn}\nAir Temp: {airtemp}°C, Water Temp: {wtrtemp}°C",
                           position=(-sel.target[0]/abs(sel.target[0]) * 20, 
                                     20),
                           anncoords="offset pixels",
                           fontsize=9, fontname="Ubuntu", color="lime",
                           backgroundcolor="lime", alpha=1)
        sel.annotation.arrow_patch.set(arrowstyle="simple", fc="lime")
        bbox = sel.annotation.get_bbox_patch()
        bbox.set_alpha(0.95)  # Set transparency level (0.0 to 1.0)
        bbox.set_facecolor('darkgreen')
    
    # Display the plot
    plt.show(block=True)

def setup_monitoring():
    print("\n\nCONFIGURATION:");
    print("91 - See monitoring configuration");
    print("92 - Add station");
    print("93 - Remove station");
    print("94 - Set data interval");
    s = input("Selection: ");
        
# Thread: Console
while (True):
    print("\n\nMENU:");
    print("10 - Help");
    print("20 - GUI: Explore Stations");
    print("30 - Start Monitoring");
    print("90 - Configuration");
    print("0 - Quit");
    s = input("Selection: ");
    if (s=='20'):
        map_thread();
    if (s=='90'):
        setup_monitoring();
    if (s=='0'):
        break;    




