#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 27 18:54:28 2024

@author: suoravi
"""

import os
import csv
import pandas as pd

def append_file(station_id, data_dict):
    filename = 'data/'+station_id+'.txt'
    
    # Check if the file exists
    file_exists = os.path.isfile(filename)
    
    # Prepare the header and new row to append
    fieldnames = data_dict.keys()
    new_row = list(data_dict.values())
    
    # If the file exists, read its current content
    if file_exists:
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)  # Read all existing rows
    else:
        rows = []  # If the file does not exist, start with an empty list
    
    # Insert the new row at the top (after the header)
    if rows:
        # Ensure the header stays in the first position, and new data comes right after
        rows = [rows[0]] + [new_row] + rows[1:]
    else:
        # If the file does not exist, we need to add the header first
        rows = [fieldnames, new_row]
    
    # Rewrite the entire file with the new row on top
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)