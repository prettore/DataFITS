import configparser
import os
import pandas as pd
from tqdm import tqdm  # progress bar
import pathlib
"""
This script takes all the data that lies in this time interval and creates one input file for each source
First define the BB, time-frame and time interval in the config.ini
"""

# Setup configuration file
configparser = configparser.RawConfigParser()
configFilePath = r'./config.ini'
configparser.read(configFilePath)

# To change the city, change the first value in the config file.
# You can see all implemented cities in the BB-Config section

# Setup city information
CITY = configparser.get('main-config', "CITY")
BB_string = configparser.get('BB-Config', CITY).replace(";", ",")  # lat1, long1, lat2, long2
BB_arr = BB_string.split(",")
BB = BB_arr[1] + "," + BB_arr[3] + "," + BB_arr[0] + "," + BB_arr[2]  # long1, long2, lat1, lat2 (FMM order)
configparser["main-config"]["bb"] = BB
with open("config.ini", "w") as configfile:
    configparser.write(configfile)  # Update BB in main_config automatically

BB = [float(numeric_string) for numeric_string in configparser.get('main-config', 'BB').split(",")]  # Get BB
TIME_START = configparser.get('main-config', 'TIME_START').replace('-', '')  # Get start time
TIME_END = configparser.get('main-config', 'TIME_END').replace('-', '')  # Get end time
TIME_INTERVAL = int(configparser.get('main-config', 'TIME_INTERVAL'))  # Get time interval

# Output the chosen setup configuration to the console
print('You chose the following setup configuration: \n')
print(f'''City: {CITY}''')
print(f'''Start: {configparser.get('main-config', 'TIME_START')}''')
print(f'''End: {configparser.get('main-config', 'TIME_END')}''')
print(f'''Time Interval: {configparser.get('main-config', 'TIME_INTERVAL')} minutes''')
print(f'''Path Variable: {configparser.get('main-config', 'path_mode')} \n''')

wdir = "data_acquisition/data/" + CITY + "/"  # Working directory

pathlib.Path("./data_enrichment/input").mkdir(parents=True, exist_ok=True)  # Create input data directory

# Iterate through all data files and create one file for each source, containing data within the defined time interval
for root, dirs, files in os.walk(wdir):
    for src in dirs:
        df = pd.DataFrame()
        if src.startswith("."):
            continue  # ignore hidden folders
        print(f'Processing {src}...')
        if src == "envirocar":
            df = pd.read_csv("data_acquisition/data/" + CITY.lower() + "/envirocar/" + CITY.lower() + "_"
                             + src.upper() + ".csv")
            df.to_csv("data_enrichment/input/" + CITY + "_" + src.upper() + ".csv", mode="w+")
            continue
        files = os.listdir(wdir + src)  # get all files from each src folder
        sorted_files = sorted(files, key=lambda x: x.split('.')[0])
        for file in tqdm(sorted_files):
            if file.startswith("."):
                continue  # ignore hidden files
            try:
                # Check if the current file matches the input time interval
                if int(TIME_END) >= int(file.split('.')[0][-8:]) >= int(TIME_START):
                    data = pd.read_csv(wdir + src + "/" + file, sep=",", index_col=[0])
                    df = pd.concat([df, data]) # add data to df
            except Exception as e:
                print(e)
                continue
        # save to input folder
        df.to_csv("data_enrichment/input/" + CITY + "_" + src.upper() + ".csv", mode="w+")
        print('\tCompleted')
