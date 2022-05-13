from datetime import time
import pandas as pd
import json
import os
import configparser
from tqdm import tqdm #for the progress bar
import time
import pathlib
import re
import ast

'''
The script is working for general traffic and incident inputs, but for some cases, we have to define more things.
E.g., Traffic and incident HERE store their coordinates with different keys
Just add your a case for the source and specify things.
'''

def write_trip_file(df,cnt):
    global SOURCE,CITY
    cords = []
    if SOURCE == "TRAFFIC_HERE":
        i=0
        #Extract the coordinates 
        counter=0
        coordinates = df[configparser.get("GPS-Config",SOURCE)]
        for entry in coordinates:
            counter+=1
            cord_arr = []
            json_data = json.loads(entry)
            json_data = json_data["streetSeg"]
            #print(json_data)
            for i in range(len(json_data)):
                for j in range(len(json_data[i])):
                    cord_arr.append([json_data[i][j]["long"],json_data[i][j]["lat"]])
                            
            cords.append(cord_arr)
            # Only take the first different cords, because they are repeated every measurment
            if counter == cnt: break
        cords = cords[:cnt]

    elif SOURCE == "INCIDENT_HERE" or SOURCE == "INCIDENT_BING":
        cord_arr = []
        Lat_From = df["incidentLat_From"]
        Long_From = df["incidentLong_From"]
        Lat_To = df["incidentLat_To"]
        Long_To = df["incidentLong_To"]
        for i in range (len(Lat_From)):
            cord_arr.append([[Long_From[i], Lat_From[i]], [Long_To[i], Lat_To[i]]])
        cords = cord_arr

    elif SOURCE == "TRAFFIC_OD":
        cords = df[configparser.get("GPS-Config",SOURCE)]
        if CITY == "KOELN":
            coordinates = []
            for entry in cords:
                coordinates.append(ast.literal_eval('[%s]' % entry))
        # Only take the first different cords, because they are repeated every measurment
            cords = coordinates
        cords = cords[:cnt]

    elif SOURCE == "CONSTRUCTION_OD":
        cords = df[configparser.get("GPS-Config",SOURCE)]

    elif SOURCE == "ENVIROCAR":
        print("Already prepared")
        return

    f = open("fmm_input/trips_"+SOURCE+".csv","w+")
    f.write("id;geom\n")
    i = 0
    print(f"Length: {cnt}")

    for i,elem in enumerate(tqdm(cords)):
        if SOURCE == "CONSTRUCTION_OD": #needs another procedure, because there are only points and not lines
            long = elem.split(",")[0][1:]
            lat = elem.split(",")[1][1:-1]
            linestr = str(i) + ";LINESTRING("
            linestr += (long + " " + lat + ",")
            linestr = linestr[:-1]
            linestr += ")"
            f.write(linestr+"\n")
            i+=1
        else:
            linestr = str(i) + ";LINESTRING("
            if SOURCE == "TRAFFIC_OD" and CITY != "KOELN":
                elem = json.loads(elem)
            if SOURCE == "TRAFFIC_OD" and CITY == "KOELN":
                for j in range(len(elem[0][0])):
                    long = elem[0][0][j][0]
                    lat = elem[0][0][j][1]
                    linestr += (str(long) + " " + str(lat) + ",")
            else:
                for j in range(len(elem)):
                    long = elem[j][0]
                    lat = elem[j][1]
                    linestr += (str(long) + " " + str(lat) + ",")
                #print(len(elem))
            linestr = linestr[:-1] #remove last comma
            linestr += ")"
            #print(linestr)
            f.write(linestr+"\n")
            i += 1


def prepare_adac(df): ### WIP ###
    time, inc_type, loc, loc_detail, desc, full_desc = [],[],[],[],[],[]
    #print(df.head())
    for index,row in df.iterrows():
        time.append(row["Time"])#[configparser.get("Timestamp-Config",SOURCE.lower())])
        inc_type.append(row["Art"])
        loc.append(row["Road No"] + ":" + row["Intersection"])
        try:
            description = row["Desc"].split(",")
            loc_detail.append(description[0])
            desc.append(description[1])
            full_desc.append(description)
        except:
            loc_detail.append(None)
            desc.append(None)
            full_desc.appen(None)
        #intersec.append()
    print(time[0])
    print(inc_type[0])
    print(loc[0])
    print(loc_detail[0])
    print(desc[0])


def prepare_data(df):
    global SOURCE, CITY
    traffic_dict = {
        "aktuell nicht ermittelbar" : int(configparser.get('Traffic-Config','no_measurement')),
        "normales Verkehrsaufkommen" : int(configparser.get('Traffic-Config','normal_traffic')),
        "erhöhte Verkehrsbelastung" : int(configparser.get('Traffic-Config','higher_traffic')),
        "Staugefahr" : int(configparser.get('Traffic-Config','traffic_jam'))
    }

    traffic_dict_koeln = {
        16 : int(configparser.get('Traffic-Config','no_measurement')),
        0 : int(configparser.get('Traffic-Config','normal_traffic')),
        1 : int(configparser.get('Traffic-Config','higher_traffic')),
        2 : int(configparser.get('Traffic-Config','traffic_jam')),
        32 : int(configparser.get('Traffic-Config','normal_traffic'))
    }

    if SOURCE == "TRAFFIC_OD" and CITY=="BONN":
        df = df.replace({'Traffic':traffic_dict})   #replace the string values with numbers
    if SOURCE == "TRAFFIC_OD" and CITY=="KOELN": 
        df = df.replace({'Traffic':traffic_dict_koeln})
    #outputDF = outputDF.replace({'speed':{0.00 : np.nan}})  #replace zero speed values with NaN, so that they wont bias the median

    for root, dirs, files in os.walk(crr_dir):
        for file in files:
            if file.startswith("."):
                continue #ignore hidden files
            if SOURCE.lower() in file.lower():
                if SOURCE.lower() == "adac":
                    pass
                    #prepare_adac(df)
                #print(SOURCE.lower())
                #print(file.lower())

                #rename time column to a unified name
                try:
                    df = df.rename(columns={configparser.get('Timestamp-Config',SOURCE.lower()):"Time"})
                except:
                    continue #already named correctly
                #remove unnamed columns
                df.drop(df.filter(regex="Unnamed"),axis=1, inplace=True)
                #overwrite input csv
                #print(f'{SOURCE} -- {df.shape}')

                df.to_csv("./input/"+file,mode="w+")
    return df


cwd = os.getcwd()
crr_dir = cwd + "/input/" #Input directory containing acquired data from all sources



#Setup config file
configparser = configparser.RawConfigParser()
configFilePath = r'../config.ini'
configparser.read(configFilePath)

Sources = configparser.options("Sources")

#Create the fmm_input and fmm_output directory
pathlib.Path("./fmm_input").mkdir(parents=True, exist_ok=True)
pathlib.Path("./fmm_output").mkdir(parents=True, exist_ok=True)


#number_of_measurements = int(configparser.get('Data-Config','NUMBER_OF_TIMESTAMPS'))  #6 = 1 hour, 144 = 1 day, #1008 = 1 week
#print(number_of_measurements)

global CITY

CITY = configparser.get('main-config', "CITY").upper()

for root, dirs, files in os.walk(crr_dir):
    for file in files:
        cnt = 0
        if file.startswith("."):
            continue #ignore hidden files
        for src in Sources:
            if src in file.lower() and CITY in file.upper():
                SOURCE = src.upper()
                print(f"Processing {SOURCE}...")
                df = pd.read_csv(crr_dir+file)

                df = prepare_data(df) #Do some things regarding data preparation

                curr_timestamp = df['Time'][0]
                for i in range (df.shape[0]):
                    timestamp = df['Time'][i] 
                    if timestamp[:15] != curr_timestamp[:15]: #compare time without seconds
                        if "TRAFFIC" in SOURCE:
                            break #special case for traffic related sources
                        else:
                            curr_timestamp = timestamp
                            cnt += 1
                if "TRAFFIC" in SOURCE:
                    cnt=i
                else:
                    cnt=i+1
                df = df[:cnt]
                #write cnt to config file:
                configparser.set('Data-Config','cnt_'+src,str(cnt))
                
                write_trip_file(df,cnt) #Creates the trip file as an input for fmm

                print('\tCompleted')

#Writes the counted values to the files
    with open('../config.ini', 'w') as configfile:
        configparser.write(configfile)
