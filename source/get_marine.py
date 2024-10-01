# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 11:48:59 2024

@author: SuorantV
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import vmath


# %% Attributes

URL_BUOY_REALTIME_ROOT = "https://www.ndbc.noaa.gov/data/realtime2/";
URL_BUOY_STATION_INFO = "https://www.ndbc.noaa.gov/data/stations/station_table.txt";
COLS = [];

# %% Methods

def get_files_from_server(URL, extension=".txt", remove_extension=True):
    # Send a GET request to the URL
    response = requests.get(URL);
    
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser');
    
    # Extract the links to files or folders
    links = []
    for link in soup.find_all('a'):
        href = link.get('href')
        if href and href != '../':  # Exclude the parent directory link
            links.append(href)
    
    # Create a DataFrame from the links
    DF_DATA = pd.DataFrame(links, columns=['Filename']);
    
    # Filter the dataframe
    DF_DATA = DF_DATA[DF_DATA['Filename'].str.contains(extension)].reset_index().drop(['index'], axis=1);
    
    # Remove the extension
    if (remove_extension):
        DF_DATA['Filename'] = DF_DATA['Filename'].str.replace('.txt', '', regex=False)
    
    return DF_DATA

def get_table_from_server(URL, header=0):
    
    DF_DATA = pd.DataFrame();
    DF_DATA = pd.read_csv(URL, delimiter="|", header=header)
    DF_DATA.columns = DF_DATA.columns.str.strip()
    
    return DF_DATA

def get_table_columns_from_server(URL, filename, extension='.txt', header=0):
        
    DF_DATA = pd.DataFrame();
    DF_DATA = pd.read_csv(URL+"/"+str(filename)+extension, 
                          delimiter="|", nrows=0).columns.tolist()

    return DF_DATA

def get_table_latest_value_from_server(URL, filename, 
                                       column, extension='.txt', 
                                       header=0, nrows=3, 
                                       firstrow=1, isnum=True):
    
    DF_DATA = pd.DataFrame();
    DF_DATA = pd.read_csv(URL+"/"+str(filename)+extension, 
                          sep="\s+", header=header, nrows=nrows);
    
    try:
        if (isnum):
            retval = pd.to_numeric(DF_DATA[column][firstrow]);
        else:
            retval = str(DF_DATA[column][firstrow]);
    except:
        retval = "N/A";
        
    return retval
    
    
def get_stations(par_selected_stations_only, par_station_list):
    global COLS;
    
    # Information and metadata related to buoys
    DF_BUOY_IDs = get_files_from_server(URL_BUOY_REALTIME_ROOT)
    DF_STATION_INFO = get_table_from_server(URL_BUOY_STATION_INFO)
    
    # Filter buoy ids to contain only the configured stations
    if (par_selected_stations_only):
      DF_BUOY_IDs = DF_BUOY_IDs[DF_BUOY_IDs['Filename'].isin(par_station_list)]
    
    # Filter the station info to contain only the buoys from which there are realtime data 
    DF_STATION_INFO = DF_STATION_INFO[DF_STATION_INFO['# STATION_ID'].isin(DF_BUOY_IDs['Filename'])].reset_index().drop(['index'], axis=1);

    # Fix the GPS format
    DF_STATION_INFO['LOCATION'] = DF_STATION_INFO['LOCATION'].str.split('(').str[0].str.strip()
    DF_STATION_INFO['LATITUDE'], DF_STATION_INFO['LONGITUDE'] = zip(*DF_STATION_INFO['LOCATION'].apply(lambda x: vmath.convert_location(x)))

    # Get the columns for the realtime data using the first available station realtime data header
    COLS = get_table_columns_from_server(URL_BUOY_REALTIME_ROOT, DF_STATION_INFO['# STATION_ID'][0])
    COLS = COLS[0].split()
    
    # print("Found %i buoys" % (len(DF_BUOY_IDs)));
    # print(DF_STATION_INFO);
    
    return DF_BUOY_IDs, DF_STATION_INFO
    
    
def get_data(station_id):
    
    global COLS;

    if not COLS:
        COLS = get_table_columns_from_server(URL_BUOY_REALTIME_ROOT, station_id)
        COLS = COLS[0].split()
    
    df = {};
    
    for COL in COLS:
        df[COL] = get_table_latest_value_from_server(URL_BUOY_REALTIME_ROOT, 
                                                     station_id,
                                                     COL)
    
    """
    df['Water Temperature'] = get_table_latest_value_from_server(URL_BUOY_REALTIME_ROOT, 
                                                 station_id,
                                                 COLS[14])
    df['Air Temperature'] = get_table_latest_value_from_server(URL_BUOY_REALTIME_ROOT, 
                                                 station_id,
                                                 COLS[13])
    df['Year'] = get_table_latest_value_from_server(URL_BUOY_REALTIME_ROOT, 
                                            station_id,
                                            COLS[0])
    df['Month'] = get_table_latest_value_from_server(URL_BUOY_REALTIME_ROOT, 
                                            station_id,
                                            COLS[1])
    df['Day'] = get_table_latest_value_from_server(URL_BUOY_REALTIME_ROOT, 
                                            station_id,
                                            COLS[2])
    df['Hour'] = get_table_latest_value_from_server(URL_BUOY_REALTIME_ROOT, 
                                            station_id,
                                            COLS[3])
    df['Minute'] = get_table_latest_value_from_server(URL_BUOY_REALTIME_ROOT, 
                                            station_id,
                                            COLS[4])
    """
    
    return df;
    
    
