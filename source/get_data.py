# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 11:48:59 2024

@author: SuorantV
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd

# %%

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

def get_table_latest_value_from_server(URL, filename, column, extension='.txt', header=0):
    
    DF_DATA = pd.DataFrame();
    DF_DATA = pd.read_csv(URL+"/"+str(filename)+extension, 
                          sep=" ", header=header, nrows=1, skiprows=1)
    
    return DF_DATA
    
    
    
    
    
    
    
    