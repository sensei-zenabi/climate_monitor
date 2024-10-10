#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct  6 21:42:13 2024

@author: suoravi
"""
import os
import pandas as pd

def print_stats_from_folder(folder_path):
    
    # Loop through all the files in the directory
    for file_name in os.listdir(folder_path):
        # Check if the file has a .txt extension
        if file_name.endswith(".txt"):
            file_path = os.path.join(folder_path, file_name)
            
            # Load the content of the txt file into a DataFrame, assuming it's delimited (e.g., by space or comma)
            df = pd.read_csv(file_path, delimiter=',', header=None)  # Adjust delimiter based on your file format
            
            # Drop columns related to time
            columns_to_drop = ['Time', 'MM', 'DD', 'hh', 'mm']
            df_clean = df.drop(columns=columns_to_drop, errors='ignore')
            
            # Drop columns where all values are NaN
            df_clean = df_clean.dropna(axis=1, how='all')
            
            # Group by Year and calculate mean and median for each numeric column
            yearly_aggregated = df_clean.groupby('#YY').agg(['mean', 'median'])
            
            # Rename the columns to include 'mean' and 'median' in the column names
            yearly_aggregated.columns = [f'{col}_{stat}' for col, stat in yearly_aggregated.columns]
            
            # Drop the first and second rows
            yearly_aggregated = yearly_aggregated.iloc[2:]
            
            print(yearly_aggregated)
