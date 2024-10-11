#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct  6 21:42:13 2024

@author: suoravi
"""
import os
import pandas as pd

def print_stats_from_folder(folder_path):
    
    first_row = True;
    df_buoys_mean = pd.DataFrame();
    df_buoys_std = pd.DataFrame();
    
    # Loop through all the files in the directory
    for file_name in os.listdir(folder_path):
        
        # Check if the file has a .txt extension
        if file_name.endswith(".txt"):
        
            file_path = os.path.join(folder_path, file_name)
            
            # Handle Buoys
            if file_name[0].isnumeric():
                
                # Load the content of the txt file into a DataFrame, assuming it's delimited (e.g., by space or comma)
                df = pd.read_csv(file_path, delimiter=',', header=0)  # Adjust delimiter based on your file format
                df = df.drop(columns=['Time', 'MM', 'DD', 'hh', 'mm']);                
                
                df_mean = df.groupby("#YY").mean()
                df_mean.insert(0, "BUOY ID", file_name.rstrip(".txt"))
                
                df_std = df.groupby("#YY").std()
                df_std.insert(0, "BUOY ID", file_name.rstrip(".txt"))
                
                df_buoys_mean = pd.concat([df_buoys_mean, df_mean], ignore_index=True)
                df_buoys_mean = df_buoys_mean.sort_values(by="BUOY ID")
                
                df_buoys_std = pd.concat([df_buoys_std, df_std], ignore_index=True)
                df_buoys_std = df_buoys_std.sort_values(by="BUOY ID")
    
    print("BUOY YEARLY MEAN VALUES:\n")
    print(df_buoys_mean.round(2).to_string(index=False))
    print("\nBUOY YEARLY STANDARD DEVIATION:\n")
    print(df_buoys_std.round(2).to_string(index=False))
    print("")