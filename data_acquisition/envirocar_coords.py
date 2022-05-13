'''
This script checks for each car of the acquired envirocar data, if the car coordinates are in a
corresponding bounding box.
This should enable a filter by city.
'''
import numpy as np
import json
import pandas as pd
import os
from geojson import Feature, MultiLineString, LineString
from geojson.feature import FeatureCollection

bb_Bonn = [["50.681209,7.064593,50.772488,7.177889"]] #Bonn // Very similar to the OpenData bounding box
bb_Cologne = [["50.910154, 6.84727, 51.021831, 7.0591"]] # Cologne // Very similar to the OpenData bounding box

#Set BB
CITY = "Cologne"
BB = bb_Cologne
BB = BB[0][0].split(",")

if (os.path.isdir('./'+CITY+'/') == False):
        os.makedirs('./'+CITY+'/')    #Creates the envirocar folder to save the data
if (os.path.isdir('./'+CITY+'/EnviroCar') == False):
        os.makedirs('./'+CITY+'/EnviroCar')    #Creates the envirocar folder to save the data

cwd = os.getcwd()

crr_dir = cwd + "/Data/"    # Data folder contains all envirocar data
cnt = 0

# Traverse the folder structure 
for root, dirs, files in os.walk(crr_dir):
    path = root.split(os.sep)
    for dir in dirs:
        # Get all trips from one car
        files = os.listdir(root+dir)
        #print(root)
        '''
        print(dir)
        print("--> Checking trips \n")
        '''

        
        # Check the first coordinates of the trip to see if they lie in the same bounding box as the desired city area
        for file in files:
            feature_collection = []
            features = []
            df = pd.read_csv(root+dir+"/"+file,encoding="utf-8", sep=";")
            # longitude - col 13; latitude - col 14
            '''
            print(df["latitude"][0])
            print(bb_Bonn[0])
            print("---------------------------")
            '''
            if any(float(BB[0]) <= item <= float(BB[2]) for item in df["latitude"]) and any(float(BB[1]) <= item <= float(BB[3])for item in df["longitude"]): #a.item(), a.any() a.all()
                str_elem = []
                if not str(df["latitude"][0]).startswith("#"):
                    print(f"{dir} drives through {CITY} on trip {file}!")
                    lat = df["latitude"]
                    lon = df["longitude"]
                    try:
                        speed = df["Speed(km/h)"]
                    except:
                        print("error with speed")
                        speed = np.zeros(len(lat))
                        #break #Should we drop the data when we dont have information about the speed?
                    for i in range (len(lat)-1):
                        str_elem = ([lon[i],lat[i]],[lon[i+1],lat[i+1]])
                        str_elem = LineString(str_elem)
                        features.append(Feature(geometry=str_elem, properties={"speed":speed[i]}))
                    feature_collection = FeatureCollection(features)

                    if len(feature_collection) != 0:
                        cnt += 1
                        print('---> writing to data_'+str(cnt)+'.json')
                        with open('./'+CITY+'/envirocar/data_'+str(cnt)+'.json', 'w+') as f:
                            json.dump(feature_collection, f)