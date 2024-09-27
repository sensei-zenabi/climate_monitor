import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt 
import mplcursors
import warnings
import threading
import os
import time

import get_marine
import get_airport
import set_data
import vmath

warnings.filterwarnings("ignore");

# %% Configuration

with open('config.py') as file:
    exec(file.read())

URL_SPACE_ROOT = "https://services.swpc.noaa.gov/text/"

warnings.filterwarnings("default");

# %% Fetch buoy data from ndbc.noaa.gov

DF_BUOY_IDs, DF_STATION_INFO = get_marine.get_stations(par_selected_stations_only,
                                                       par_station_list);

# %% Append airport data to the station info dataframe

for airport in par_airport_list:
    DF_AIRPORTS = get_airport.get_data(airport);
    DF_STATION_INFO.loc[len(DF_STATION_INFO)] = ['99999','','Airport','',DF_AIRPORTS['location'],'',airport,'','','',DF_AIRPORTS['latitude'],DF_AIRPORTS['longitude']];


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
    
    # Fetch data by mouse click
    @cursor.connect("add")
    def on_add(sel):
        station_id = DF_STATION_INFO.iloc[sel.index]['# STATION_ID']
        ttype = DF_STATION_INFO.iloc[sel.index]['TTYPE']
        location = DF_STATION_INFO.iloc[sel.index]['LOCATION']
        if (station_id != '99999'):
            dft = get_marine.get_data(station_id);
            sel.annotation.set(text=f"ID: {station_id} - {ttype}\nLocation: {location}\nLast Confirmed Time: {dft['#YY']}-{dft['MM']}-{dft['DD']} {dft['hh']}:{dft['mm']}\nAir Temp: {dft['ATMP']}°C, Water Temp: {dft['WTMP']}°C",
                               position=(-sel.target[0]/abs(sel.target[0]) * 20, 
                                         20),
                               anncoords="offset pixels",
                               fontsize=9, fontname="Ubuntu", color="lime",
                               backgroundcolor="lime", alpha=1)
        
        if (station_id == '99999'):
            dft = get_airport.get_data(location);
            sel.annotation.set(text=f"ID: {ttype}\nLocation: {location}\nLast Confirmed Time: {15}\nAir Temp: {dft['temperature_C']}°C, Humidity: {dft['relative_humidity']}\nWind Speed: {dft['wind_speed_m_s']}mPsec, Pressure: {dft['pressure_hPa']}hPa",
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

def monitoring_thread():
    time_entry = os.times().elapsed;
    running = True;
    while (running):
        time_elapsed = os.times().elapsed - time_entry;
        print('Time remaining: %.0fs' % (60*par_monitoring_interval - time_elapsed)) 
        time_stamp = os.times().elapsed;
        if (time_elapsed >= 60*par_monitoring_interval):
            print("\nFetching data...");
            for station_id in DF_STATION_INFO['# STATION_ID']: 
                if (station_id != '99999'):
                    print("Updating " + station_id + "...")
                    dft = get_marine.get_data(station_id); 
                    set_data.append_file(station_id=station_id, 
                                         data_dict=dft)
            time_entry = os.times().elapsed;
        while ( (os.times().elapsed - time_stamp) <= 1.0):
            # do nothing
            time.sleep(0.01)            
            
# Thread: Console
while (True):
    print("\n\nMENU:");
    print("10 - Help");
    print("20 - GUI: Explore Stations");
    print("30 - Start Monitoring");
    # print("90 - Configuration");
    print("0 - Quit");
    s = input("Selection: ");
    if (s=='20'):
        map_thread();
    if (s=='30'):
        monitoring_thread();
    if (s=='0'):
        break;    




