from re import I
import pandas as pd
from ast import literal_eval
import numpy as np
import os
import configparser
from tqdm import tqdm #for the progress bar
import sys
import dateutil.parser as parser
from datetime import timedelta
'''
- Read test_bingIncident as input file
- Traverse through all rows, collect each cpath/cpath entry
- output a new csv file, where the data entries are indexed by FIDs of the cpath arrays
'''

def floor_minutes(dt, mins):
    # First zero out seconds and micros
    dtTrunc = dt.replace(second=0, microsecond=0)

    # Figure out how many minutes we are past the last interval
    passedMinutes = (dtTrunc.hour*60 + dtTrunc.minute) % mins

    # Subtract off the excess minutes to get the last interval
    return dtTrunc + timedelta(minutes=-passedMinutes)



finished_sources = []

def construct_df(SOURCE):
    col_filter = None
    global finished_sources, CITY, PATH_MODE
    #setup a filter, only taking the necessary columns. This is done to safe memory
    if SOURCE == "INCIDENT_BING":
        file = "./output/test_"+SOURCE+".csv"
        col_filter = ["Time","incidentID","incidentType","incidentComments",PATH_MODE,"origin_ids"]
    elif SOURCE =="INCIDENT_HERE":
        file = "./output/test_"+SOURCE+".csv"
        col_filter = ["Time","incidentID","incidentType","incidentComments",PATH_MODE,"origin_ids"]
    elif SOURCE == "CONSTRUCTION_OD":
        file = "./output/test_"+SOURCE+".csv"
        #filter can be implemented later; care because columns have different names respectively for the city
    elif SOURCE =="TRAFFIC_HERE":
        file = "./output/test_"+SOURCE+".csv"
        col_filter = ["Time","JF","SP",PATH_MODE,"origin_ids"]
    elif SOURCE =="TRAFFIC_OD":
        file = "./output/test_"+SOURCE+".csv"
        #filter can be implemented later; care because columns have different names respectively for the city
    elif SOURCE =="ENVIROCAR":
        file = "./output/test_"+SOURCE+".csv"
    #elif SOURCE =="ADADC":
        #file = "./output/test_"+SOURCE+".csv"

    try:
        if col_filter != None:
            #load csv file with columns regarding the selected filter into a dataframe
            df = pd.read_csv(file, usecols = col_filter)#read df with filter if set
            #df[['JF','SP']] == df[['JF','SP']].astype('float32') #Change float64 to float32 to save some memory
        else:
            #load complete csv file into a dataframe
            df = pd.read_csv(file)
        new_array = []
        for index, row in df.iterrows():
            index_list = []
            row[PATH_MODE] = literal_eval(row[PATH_MODE])
            for val in row[PATH_MODE]:                # check every value of cpath 
                index_list.append(val)   
            new_array.append([index, list(set(index_list))])   # contains all cpath values of one id

    except:
        print("ERROR iterating through df and selecting " + PATH_MODE + " values")
    
    floats = df.select_dtypes(include=['float64']).columns.tolist()
    df[floats] = df[floats].astype('float32')

    #df.info(memory_usage="deep")
    #print(str(sys.getsizeof(new_array)/2**20) + "MB") #.info(memory_usage="deep")

    origin_ids = []
    pathIDs = []
    indexes = []
    sources = []
    times = []
    path_values = []
    traffic = []
    speed = []
    incident_id = []
    incident_type = []
    incident_comments = []
    #construction_reason = []
    construction_blockage = []
    fuel_consumption = [] #per h
    rpm = [] #u/min
    throttle_pos = [] #in %
    co2 = [] #kg/h
    vehicle_id = []
    street_desc = []


    features = []
    i=0

    df = df.reset_index() #Resets the index values (needed, if one/more entries got dropped in fmm_to_json.py)

    traffic_indicators = {      #contains the labels for the different traffic columns
        "TRAFFIC_HERE" : "JF",
        "TRAFFIC_OD" : "Traffic",
    }

    speed_indicators = {        #contains the labels for the different speed columns
        "TRAFFIC_HERE" : "SP",
        "TRAFFIC_OD" : "Speed",
        "ENVIROCAR" : "GPS Speed(km/h)"
    }

    for index,path in tqdm(new_array):
        for i in range (len(path)):
            #print(f"{i} -- {cpath[i]}: New FID")
            origin_ids.append(df.iloc[index]["origin_ids"])
            pathIDs.append(path[i])
            indexes.append(index)
            sources.append(SOURCE)
            #convert time value and add it to final dataset
            if FLOOR_TIME:
                #Floor the time value to 10 minute intervals
                times.append(floor_minutes(parser.parse(df.iloc[index]["Time"]).replace(microsecond=0,tzinfo=None), 10).isoformat())
            else:
                times.append(parser.parse(df.iloc[index]["Time"]).replace(microsecond=0,tzinfo=None).isoformat())

            path_values.append(path)
            if "ENVIROCAR" in SOURCE:
                fuel_consumption.append(df.iloc[index]["Consumption(l/h)"])
                rpm.append(df.iloc[index]["Rpm(u/min)"])
                throttle_pos.append(df.iloc[index]["Throttle Position(%)"])
                co2.append(df.iloc[index]["CO2(kg/h)"])
                vehicle_id.append(df.iloc[index]["vehicle_id"])
            else:
                fuel_consumption.append(None)
                rpm.append(None)
                throttle_pos.append(None)
                co2.append(None)
                vehicle_id.append(None)
            if SOURCE in traffic_indicators:
                traffic.append(df.iloc[index][traffic_indicators[SOURCE]])
                if SOURCE == "TRAFFIC_HERE":
                    #street_desc.append(df.iloc[index]["streetIntersection"])
                    construction_blockage.append(None)
                elif SOURCE == "TRAFFIC_OD" and CITY == "KOELN":
                    try:
                        construction = df.iloc[index]["Link"]
                    except:
                        construction = None
                    construction_blockage.append(construction)
                    #street_desc.append(None)
            else:
                traffic.append(None)
            if "CONSTRUCTION" in SOURCE and CITY == "BONN":
                incident_id.append(df.iloc[index]["Construction Id"])
                #street_desc.append(df.iloc[index]["Desc"])
                incident_type.append(df.iloc[index]["Reason"])              # equal to incidentType
                construction_blockage.append(df.iloc[index]["Blockage"])
            elif "CONSTRUCTION" in SOURCE and CITY == "KOELN":
                incident_id.append(df.iloc[index]["Construction Id"])
                #street_desc.append(df.iloc[index]["Adress"])
                incident_type.append(df.iloc[index]["Typ"])
            elif SOURCE != "TRAFFIC_HERE" and (SOURCE != "TRAFFIC_OD" or CITY != "KOELN"):
                #street_desc.append(None)
                construction_blockage.append(None)
            if SOURCE in speed_indicators:
                try:
                    speed.append(df.iloc[index][speed_indicators[SOURCE]])  #only append if speed value exists in data
                except:
                    speed.append(None)
            else:
                speed.append(None)
            if "INCIDENT" in SOURCE:
                incident_id.append(df.iloc[index]["incidentID"])
                incident_type.append(df.iloc[index]["incidentType"])
                incident_comments.append(df.iloc[index]["incidentComments"])
            else:
                if SOURCE != "CONSTRUCTION_OD":
                    incident_id.append(None)
                    incident_type.append(None)
                incident_comments.append(None)
    
    del(df)         #remove to save memory
    del(new_array)  #remove to save memory

    #print(len(street_desc), len(construction_blockage), len(traffic), len(times)) 
    # removed col "street_desc":street_desc,
    df1 = pd.DataFrame({PATH_MODE+"_id":pathIDs, "origin_id":origin_ids, "source":sources, "time":times, 
                        "speed":speed, "traffic":traffic, "incidentType":incident_type, 
                        "incidentID":incident_id, "incidentComments":incident_comments, 
                        "Construction Blockage":construction_blockage ,"Consumption(l/h)":fuel_consumption,
                        "Rpm(u/min)":rpm, "Throttle Position(%)":throttle_pos, "CO2(kg/h)":co2, "vehicle_id":vehicle_id, "id":indexes, PATH_MODE:path_values})
    #print(df1.head)

    #maybe this duplicate removal is not necessary
    df1 = df1.drop_duplicates(subset=["id",PATH_MODE+"_id","source"])    # there are some duplicates, due to cpath values occuring multiple times
                                                                    # maybe change this all to usage of cpath values 
    finished_sources.append(SOURCE)

    return df1



def group_entries(df):
    global PATH_MODE
    '''
    Gets the complete dataframe and should output a new df, which groups the entries
    with the same fid and adds all the data
    Problem: Traffic related sources can have different speed values etc.
        - Maybe take the average
        - Just take the one from HERE?
    '''

    #aggregation_functions = {'cpath_id': 'first', 'source': 'add', 'time':'first', 'cpath': 'first',
    #                        'speed':'first', 'traffic':'first', 'incidentType':'first', 
    #                        'incidentCriticality':'first', 'incidentComments':'first' }

    df = df.sort_values(by=[PATH_MODE+'_id'])

    #changes the source column by joining the strings with the same fid/cpath_id
    df["source"] = df[["source"]].groupby(df[PATH_MODE+'_id'])['source'].transform(lambda x: ",".join(x))
    #groups the rows with the same cpath_ids and adds missing cells
    df = df.groupby([PATH_MODE+'_id']).agg({'source' : 'first',
                                        'speed' : np.median,
                                        'traffic' : np.median,
                                        'time' : 'first',
                                        'incidentType':'first', 
                                        'incidentCriticality':'first', 
                                        'incidentComments':'first'}) #cpath is removed here because how to handle?

    return df



#Setup config file
configparser = configparser.RawConfigParser()
configFilePath = r'../config.ini'
configparser.read(configFilePath)

# Read data from config file
global CITY, PATH_MODE, FLOOR_TIME
CITY = configparser.get('main-config', "CITY").upper()
PATH_MODE = configparser.get('main-config', "path_mode")
FLOOR_TIME = True
Sources = configparser.options("Sources")

outputDF = pd.DataFrame(columns=["source", "time", "speed", "traffic", "street_desc", 
                                "incidentType", "incidentID", "incidentComments", "Construction Blockage", 
                                "Consumption(l/h)","Rpm(u/min)","Throttle Position(%)","CO2(kg/h)","vehicle_id", PATH_MODE+"_id", "origin_id", PATH_MODE])  #columns need to have the same name as in the df1

#create a new output file
write_mode = "w+"
header_mode = True

for source in Sources:
    SOURCE = source.upper()
    print(f'--- Processing data from {SOURCE} ---')
    #if SOURCE == "CONSTRUCTION_OD":
        #continue   #only because the data is not contained in the old acquisitions
    if SOURCE == "ADAC":
        print("ADAC data processing not implemented yet")
        continue
    if SOURCE == "WEATHER":
        print("Weather data processing is not implemented yet")
        continue
    df = construct_df(SOURCE)
    #outputDF = outputDF.append(df)
    df.to_csv("output/output_total.csv",mode=write_mode,header=header_mode)
    #After the file has been created we switch to append mode
    write_mode = "a"
    header_mode = False