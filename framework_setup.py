'''
User should setup the BB, time-frame and time interval in the setup.ini
This script takes all the data that lies in this time interval and creates one input file for each source
'''
import configparser
import os
import pandas as pd
from tqdm import tqdm #for the progress bar
import pathlib
import time

#Setup config file
configparser = configparser.RawConfigParser()
configFilePath = r'./config.ini'
configparser.read(configFilePath)

CITY = configparser.get('main-config', "CITY")
BB_string = configparser.get('BB-Config',CITY).replace(";",",")	#lat1, long1, lat2, long2
BB_arr = BB_string.split(",")
BB = BB_arr[1]+","+BB_arr[3]+","+BB_arr[0]+","+BB_arr[2]	#long1, long2, lat1, lat2 (This is needed for mapmatching)
configparser["main-config"]["bb"] = BB
with open("config.ini","w") as configfile:
	configparser.write(configfile)	#Write the user defined BB from Config-BB automatically in the main_config as the current used BB
BB = [float(numeric_string) for numeric_string in configparser.get('main-config','BB').split(",")] #Get Bounding Box
TIME_START = configparser.get('main-config', 'TIME_START').replace('-','') #Get start time
TIME_END = configparser.get('main-config', 'TIME_END').replace('-','') #Get end time
TIME_INTERVAL = int(configparser.get('main-config', 'TIME_INTERVAL')) #Get time interval

print('You chose the following setup configuration: \n')
print(f'''City: {CITY}''')
print(f'''Start: {configparser.get('main-config', 'TIME_START')}''')
print(f'''End: {configparser.get('main-config', 'TIME_END')}''')
print(f'''Time Interval: {configparser.get('main-config', 'TIME_INTERVAL')} minutes \n''')

wdir = "../complete_data/"+CITY+"/" #Working directory

#Create the input directory
pathlib.Path("./data_enrichment/input").mkdir(parents=True, exist_ok=True)


for root, dirs, files in os.walk(wdir):
	for src in dirs:
		df = pd.DataFrame()
		if src.startswith("."):
			continue #ignore hidden folders
		print(f'Processing {src}...')
		files = os.listdir(wdir+src) #get all files from each src folder
		sorted_files = sorted(files, key=lambda x: x.split('.')[0])
		for file in tqdm(sorted_files):
			if file.startswith("."):
				continue #ignore hidden files
			try:
				if (int(TIME_END) >= int(file.split('.')[0][-8:]) >= int(TIME_START)): #only take entries that are in the given time frame
					df = df.append(pd.read_csv(wdir+src+"/"+file, sep=",")) #add to src_df
			except:
				continue
		#save to input folder
		df.to_csv("data_enrichment/input/"+CITY+"_"+src.upper()+".csv",mode="w+")
		print('\tCompleted')