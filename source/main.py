import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt 
import warnings
import threading
import os
import time
from datetime import datetime, timedelta

import get_marine
import get_airport
import store_data
import process_data
import vmath
import terminal_map

warnings.filterwarnings("ignore");
os.system('clear');

# %% Configuration

with open('config.py') as file:
    exec(file.read())

URL_SPACE_ROOT = "https://services.swpc.noaa.gov/text/"

warnings.filterwarnings("default");

# %% Retrieve station info

s = input("\nDo you wish to update the STATION INFO file? [y/n]: ");
if (s=="y"):
    # Fetch buoy data from ndbc.noaa.gov
    print("FETCHING BUOY DATA...");
    DF_BUOY_IDs, DF_STATION_INFO = get_marine.get_stations(par_selected_stations_only,
                                                           par_station_list);
    print("Found %i buoys" % (len(DF_STATION_INFO)));
    
    # Append airport data to the station info dataframe
    print("\nFETCHING AIRPORT DATA...");
    i=1;
    for airport in par_airport_list:
        DF_AIRPORTS = get_airport.get_data(airport);
        DF_STATION_INFO.loc[len(DF_STATION_INFO)] = ['99999','','Airport','',DF_AIRPORTS['location'],'',airport,'','','',DF_AIRPORTS['latitude'],DF_AIRPORTS['longitude']];
        i+=1;
    
    # Prompt user about saving the station list to file
    print("Found %i airports" % (i));
    s = input("\nDo you wish to save the STATION INFO file? [y/n]: ");
    if (s=="y"):
        print("Writing data/station_info.txt ...");
        DF_STATION_INFO.to_csv('data/station_info.txt', sep=';', index=False)
else:
    print('Loading the saved STATION INFO file...');
    try:
        DF_STATION_INFO = pd.read_csv('data/station_info.txt', sep=';');
    except:
        print("ERROR! Cannot find station info file!")
        print("Exiting program...");
        exit();

# %% APP - STATION BROWSER
# For maps: https://www.naturalearthdata.com/downloads/110m-cultural-vectors/
# For annotations: https://mplcursors.readthedocs.io/en/stable/examples/change_popup_color.html

# Thread: Print Stations
def print_stations_thread():
    os.system("clear");
    print('MONITORED STATIONS:\n')
    print(DF_STATION_INFO[["# STATION_ID","LOCATION","NAME"]].to_string());
    input("\nPress any key to continue...");

# Thread: Terminal Map
def terminal_map_thread():
    terminal_map.display_map(DF_STATION_INFO, "LATITUDE", "LONGITUDE", 
                             additional_info_1="# STATION_ID",
                             additional_info_2="LOCATION");

# Thread: Visualization
def statistics_thread():
    os.system('clear');
    print('STATISTICS\n')
    process_data.print_stats_from_folder('data/');
    input('Press any key to continue...');

# Thread: Monitoring
def monitoring_thread():
    # Do nothing
    os.system('clear');
    time_stamp_screen = os.times().elapsed;
    time_stamp_data = os.times().elapsed;
    refresh_interval = par_monitoring_interval * 60;
    running = True; first_run = True;
    while (running):
        time_screen_refresh = os.times().elapsed - time_stamp_screen; 
        if (time_screen_refresh >= refresh_interval or first_run):
            first_run = False;
            os.system('clear');
            # Draw UI
            print("STATION MONITOR");
            print("Last update: %s - Next update: %s\n" % (datetime.now(), datetime.now()+timedelta(seconds=refresh_interval)));
            for index in DF_STATION_INFO.index:
                station_id = str(DF_STATION_INFO.iloc[index]['# STATION_ID'])
                dft_all = []; output_text = "";
                if (station_id != '99999'):
                    # Print BYOU data to the screen
                    dft = get_marine.get_data(station_id);
                    output_text += "BUOY " + station_id + " ";
                    output_text += "| Water Direction [deg]: %3.3s " % (dft["WDIR"]);
                    output_text += "| Water Speed [m/s]: %4.4s " % (dft["WSPD"]);
                    output_text += "| Temperature Air / Water [degC]: %4.4s / %4.4s " % (dft["ATMP"],dft["WTMP"]);
                    output_text += "| Pressure [hPa]: %4.4s" % (dft["PRES"]);
                    print(output_text);
                    store_data.append_file(station_id=station_id, 
                                         data_dict=dft)
                if (station_id == '99999'):
                    # Print AIRPORT data to the screen
                    location = DF_STATION_INFO.iloc[index]['LOCATION']
                    dft = get_airport.get_data(location);
                    output_text += "%22.22s " % (dft["location"]) ;
                    output_text += "| Wind Spd. [m/s]: %3.3s " % (dft["wind_speed_m_s"]);
                    output_text += "| Visb. [km]: %4.4s " % (dft["visibility_km"]);
                    output_text += "| Air Temp. [degC]: %4.4s " % (dft["temperature_C"]);
                    output_text += "| Rel. Hmd. [prcnt]: %3.3s " % (dft["relative_humidity"]);
                    output_text += "| Pres. [hPa]: %4.4s " % (dft["pressure_hPa"]);
                    print(output_text);
                    store_data.append_file(station_id=location, 
                                         data_dict=dft)
            print('\nFinished fetching data. Waiting for next scheduled query...')
            # Update time stamp of last screen refresh
            time_stamp_screen = os.times().elapsed;
        time.sleep(0.1);

# Thread: Console
while (True):
    os.system('clear');
    print("\n\nMENU:");
    print("10 - Print STATION INFO");
    print("20 - Show Stations over ASCII Map");
    print("30 - Display Statistics");
    print("40 - Start Station Monitoring");
    print("0 - Quit");
    s = input("Selection: ");
    if (s=='10'):
        print_stations_thread();
    if (s=='20'):
        terminal_map_thread();
    if (s=='30'):
        statistics_thread();
    if (s=='40'):
        monitoring_thread();
    if (s=='0'):
        break;




