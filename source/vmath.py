# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 13:11:36 2024

@author: SuorantV
"""

def convert_location(location_str):
    lat_str, lat_dir, lon_str, lon_dir = location_str.split()
    
    # Convert latitude
    latitude = float(lat_str)
    if lat_dir == 'S':
        latitude = -latitude
    
    # Convert longitude
    longitude = float(lon_str)
    if lon_dir == 'W':
        longitude = -longitude
    
    return latitude, longitude