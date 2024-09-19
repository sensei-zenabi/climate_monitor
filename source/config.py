#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 17 21:57:35 2024

@author: suoravi
"""

import pandas as pd
import configparser

config = configparser.ConfigParser();
config.read('config.ini');

# Read the config
par_monitoring_interval = int(config['Settings']['monitoring_interval']);
par_selected_stations_only = int(config['Settings']['selected_stations_only']);

par_station_list = config['Stations']['station_list'].split(',');
par_station_list = [item.strip() for item in par_station_list];

par_airport_list = config['Stations']['airport_list'].split(',');
par_airport_list = [item.strip() for item in par_airport_list];
