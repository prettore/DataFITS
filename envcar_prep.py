import json
from geojson import Feature, MultiLineString, LineString
from geojson.feature import FeatureCollection
import re
import numpy as np
import pandas as pd
import os
import configparser
from tqdm import tqdm #for the progress bar
import shutil

'''
To change the city, change the first value in the config file. You can see all implemented cities in the BB-Config section
'''

SOURCE = "ENVIROCAR"

def remove_trips(BB):
    output_folder = "envirocar/Data_Cut"
    if os.path.isdir("envirocar/Data_Cut/"):
        shutil.rmtree("envirocar/Data_Cut")
    os.mkdir("envirocar/Data_Cut/")
    print("Checking envirocar files...")
    i=0
    i_dir = 0
    for root, dirs, files in os.walk("envirocar/Data/"):
        for dir in dirs:
            i_dir += 1
            files = os.listdir(root+dir)
            for file in files:
                print(f"Found {i} matching file(s) in {i_dir}/{len(dirs)} folders",end='\r')
                #try:
                df = pd.read_csv(root+dir+"/"+file,encoding="utf-8", sep=";")
                #print(df.columns)
                #except:
                    #print(f"Error reading file {file} in {dir}")
                if any(float(BB[0]) <= item <= float(BB[1]) for item in df["longitude"]) and any(float(BB[2]) <= item <= float(BB[3])for item in df["latitude"]): #a.item(), a.any() a.all()
                    i+=1 
                    new_df = pd.DataFrame()
                    for index, row in df.iterrows():
                        if float(BB[0]) <= float(row["longitude"]) <= float(BB[1]) and float(BB[2]) <= float(row["latitude"]) <= float(BB[3]): 
                            #check if the data is in the correct timestamp
                            #if (int(TIME_END) >= int(row["time"][0:10].replace("-","")) >= int(TIME_START)): 
                            new_df = new_df.append(df.iloc[index])
                            if not os.path.isdir("envirocar/Data_Cut/"+dir):
                                os.mkdir("envirocar/Data_Cut/"+dir)
                            new_df.to_csv("envirocar/Data_Cut/"+dir+"/"+file)
                            print(f"Found {i} matching file(s) in {i_dir}/{len(dirs)} folders",end='\r')
    print(f"Found {i} matching file(s)")


def create_fmm_for_one_trip():
    print("Creating trip file...")
    f = open("./data_enrichment/fmm_input/trips_"+SOURCE+".csv","w+")
    f.write("id;geom\n")
    total_id = 0
    counter=0
    total_id_arr = []
    total_df = pd.DataFrame()
    total_df.insert(0,"total_id","")
    for root, dirs, files in os.walk("envirocar/Data_Cut/"):
        for dir in dirs:
            files = os.listdir(root+dir)
            for file in files:
                try:
                    #Read each file from a trip
                    df = pd.read_csv(root+dir+"/"+file,encoding="utf-8", sep=",")
                    assert (len(df) > 2)    #if the file does not contain valid information go to except statement
                    for i in range (len(df)):
                        total_id_arr.append(total_id)
                        total_id += 1
                    #df.to_csv("./data_enrichment/input/Bonn_Envirocar.csv")
                except:
                    print(f"Error reading file {file} in {dir}")
                    break
                cord_arr = []
                for i in range(len(df)):
                    cord_arr.append([df["latitude"][i],df["longitude"][i]])
                
                f = open("./data_enrichment/fmm_input/trips_"+SOURCE+".csv",mode="a")
                for elem in cord_arr:
                    linestr = str(counter) + ";LINESTRING("
                    lat = elem[0]
                    long = elem[1]
                    linestr += (str(long) + " " + str(lat) + ",")
                    linestr = linestr[:-1] #remove last comma
                    linestr += ")"
                    f.write(linestr+"\n")
                    counter+=1
                total_df = total_df.append(df)
                total_df["total_id"] = total_id_arr
                #print(f"{dir} / {file} done'")
                #break
            #break
        #break
        total_df["total_id"] = total_id_arr
        total_df = total_df.loc[:, ~total_df.columns.str.contains('^Unnamed')]
        total_df.to_csv("./data_enrichment/input/"+CITY+"_ENVIROCAR.csv",mode="w+")



def fuse_fmm_and_data(df):
    features = []
    feature_collection = []
    counter = 0

    ids = []
    opath_arr = []
    cpath_arr = []
    csv_cords = []

    input_df = pd.read_csv("./data_enrichment/fmm_output/output_Envirocar.csv", sep=";")
    input_df = input_df.sort_values(by=["id"])
    input_df.to_csv("./data_enrichment/fmm_output/output_"+SOURCE+".csv", sep=";", index=False)

    f = open("./data_enrichment/fmm_output/output_"+SOURCE+".csv","r")
    next(f)

    wrongEntry_IDs = []

    for line in f.readlines():
        fid = int(line.split(";")[0])   # gets the id value of the entry
        opath = line.split(";")[1]      # gets the opath values of the entry
        if len(opath) == 0:             # if there is no opath value, there was a problem in the fmm process
            print(f"!! ERROR in line {counter} with the following content: {line[:-1]} !!")
            opath="-1"
            cpath="-1"
            wrongEntry_IDs.append(counter)  # add the ID of the problematic entry, to later drop it
            counter += 1
            continue
            #Then there is no matched road
        else:
            cpath = line.split(";")[2]  # if there is no problem, continue getting the cpath values

        line = line.split("LINESTRING")[1]
        cords = []
        cords = re.findall(r'\d+[.,]\d*', line)
        cords = [float(i) for i in cords]
        str_elem = []
        for i in range (0,len(cords)-1,2):
            str_elem += ([[cords[i], cords[i+1]]])
        ids.append(fid)                                                         # add the id of the value to a new id array
        opath_arr.append(list(set([int(opath_val) for opath_val in opath.split(",")])))    # add the numeric values to a new array and remove double entries
        cpath_arr.append([int(cpath_val) for cpath_val in cpath.split(",")])    # add the numeric values to a new array
        csv_cords.append(str_elem)                                              # add the coordinates to a array
        str_elem = LineString(str_elem)
        features.append(Feature(geometry=str_elem, properties={"fid":fid}))
        counter += 1
    feature_collection = FeatureCollection(features)

    # Export the geojson file to the output destination
    with open("./data_enrichment/geojson_output/"+"geojson_envirocar.json","w+") as f:
        json.dump(feature_collection, f)

    '''
    Drop all entries that had an error on fmm
    PROBLEM: This will cause missing indexes, but it is handled in all further scripts
    '''
    for entry in wrongEntry_IDs:
        df = df.drop(index=entry)


    ids = sorted(ids)           # add new columns from the original df to the resulting df
    df["id"] = ids              # this is only representing the id of each separate data source //not the real fid of a road segmnet related with the shapefile
    df["opath"] = opath_arr    
    df["cpath"] = cpath_arr
    df["new_cords"] = csv_cords

    df = df.set_index("id") # Sets the column id as index

    #df.append({"fid":ids, "cords":csv_cords}, ignore_index=True)
    df.to_csv("./data_enrichment/output/test_"+SOURCE+".csv")
    print(f"--> {SOURCE} completed")

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

remove_trips(BB)
create_fmm_for_one_trip()


        