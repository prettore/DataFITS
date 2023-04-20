import configparser
import shutil
import numpy as np
import json
import pandas as pd
import os
from geojson import Feature, MultiLineString, LineString
from geojson.feature import FeatureCollection
import data_acquisition.envirocar_acuisition as collect_data
"""
This script collects all available envirocar data and processes it by extracting the information
by each city and storing it to csv files 
"""


def filter_data(BB):
    global CITY
    """
    This script checks for each car of the acquired envirocar data, if the car coordinates are in a
    corresponding bounding box. This serves as a filter by city.
    """

    if not os.path.isdir('data_acquisition/envirocar_data/' + CITY + '/'):
        os.makedirs('data_acquisition/envirocar_data/' + CITY + '/')  # Creates the envirocar folder to save the data

    # Setup working directory
    cwd = os.getcwd()
    crr_dir = "data_acquisition/envirocar_data/total/"  # Data folder contains all envirocar data
    cnt = 0

    print(f"Processing Data for {CITY} ...")
    # Traverse the folder structure
    for root, dirs, files in os.walk(crr_dir):
        path = root.split(os.sep)
        for dir in dirs:
            # Get all trips from one car
            files = os.listdir(root + dir)
            # Check the first coordinates of the trip to see if they lie in the same bounding box as the desired city area
            for file in files:
                feature_collection = []
                features = []
                df = pd.read_csv(root + dir + "/" + file, encoding="utf-8", sep=";")
                if any(float(BB[0]) <= item <= float(BB[2]) for item in df["latitude"]) and any(
                        float(BB[1]) <= item <= float(BB[3]) for item in df["longitude"]):
                    str_elem = []
                    if not str(df["latitude"][0]).startswith("#"):
                        # print(f"{dir} drives through {CITY} on trip {file}!")
                        lat = df["latitude"]
                        lon = df["longitude"]
                        try:
                            speed = df["Speed(km/h)"]
                        except:
                            # print("error with speed")
                            speed = np.zeros(len(lat))
                            # break #Should we drop the data when we don't have information about the speed?
                        for i in range(len(lat) - 1):
                            str_elem = ([lon[i], lat[i]], [lon[i + 1], lat[i + 1]])
                            str_elem = LineString(str_elem)
                            features.append(Feature(geometry=str_elem, properties={"speed": speed[i]}))
                        feature_collection = FeatureCollection(features)

                        if len(feature_collection) != 0:
                            cnt += 1
                            # print('---> writing to data_' + str(cnt) + '.json')
                            with open('data_acquisition/envirocar_data/' + CITY + '/data_' + str(cnt) + '.json',
                                      'w+') as f:
                                json.dump(feature_collection, f)


def collect_trips(BB):
    global CITY
    """
    Extracts ENVIROCAR data related to the processed city
    """
    if not os.path.isdir('data_acquisition/envirocar_data/' + CITY + '/'):
        os.makedirs('data_acquisition/envirocar_data/' + CITY + '/')  # Creates the envirocar folder to save the data

    if os.path.isdir('data_acquisition/envirocar_data/' + CITY + '/'):
        shutil.rmtree('data_acquisition/envirocar_data/' + CITY + '/')
    os.mkdir('data_acquisition/envirocar_data/' + CITY + '/')

    print(f"Checking envirocar files for {CITY} ...")
    i = 0
    i_dir = 0
    for root, dirs, files in os.walk("data_acquisition/envirocar_data/total/"):
        for dir in dirs:
            i_dir += 1
            files = os.listdir(root + dir)
            for file in files:
                print(f"\rFound {i} matching file(s) in {i_dir}/{len(dirs)} folders", end='')
                # try:
                df = pd.read_csv(root + dir + "/" + file, encoding="utf-8", sep=";")
                # print(df.columns)
                # except:
                # print(f"Error reading file {file} in {dir}")
                if any(float(BB[0]) <= item <= float(BB[1]) for item in df["longitude"]) and any(
                        float(BB[2]) <= item <= float(BB[3]) for item in
                        df["latitude"]):  # a.item(), a.any() a.all()
                    i += 1
                    new_df = pd.DataFrame(columns=['time', 'id', 'CO2(kg/h)', 'GPS Altitude(m)', 'GPS Bearing(deg)',
                                                   'GPS HDOP(precision)', 'Consumption(l/h)', 'MAF(l/s)', 'Speed(km/h)',
                                                   'GPS Speed(km/h)', 'Rpm(u/min)', 'Throttle Position(%)',
                                                   'GPS VDOP(precision)', 'Intake Pressure(kPa)', 'GPS PDOP(precision)',
                                                   'GPS Accuracy(%)', 'Intake Temperature(c)', 'Engine Load(%)',
                                                   'longitude', 'latitude', 'vehicle_id'])
                    for index, row in df.iterrows():
                        if float(BB[0]) <= float(row["longitude"]) <= float(BB[1]) and float(BB[2]) <= float(
                                row["latitude"]) <= float(BB[3]):
                            # check if the data is in the correct timestamp
                            # if (int(TIME_END) >= int(row["time"][0:10].replace("-","")) >= int(TIME_START)):
                            # if (int(TIME_START) <= int(row["time"][0:10].replace("-",""))):
                            new_df = pd.concat([new_df, df.iloc[[index]]], axis=0, ignore_index=True)
                        if not os.path.isdir("data_acquisition/envirocar_data/" + CITY + "/" + dir):
                            os.mkdir("data_acquisition/envirocar_data/" + CITY + "/" + dir)
                        new_df.to_csv(
                            "data_acquisition/envirocar_data/" + CITY + "/" + dir + "/" + row["time"][0:10].replace("-",
                                                                                                                    "") + "_" + file)
                        print(f"\rFound {i} matching file(s) in {i_dir}/{len(dirs)} folders", end='')
    print("\n")


def create_trip_file():
    global CITY
    """
    Creates the input file for FMM of Envirocar data
    """

    if os.path.isdir('data_acquisition/data/' + CITY + '/envirocar/'):
        shutil.rmtree('data_acquisition/data/' + CITY + '/envirocar/')
    os.mkdir('data_acquisition/data/' + CITY + '/envirocar/')

    print("Combining data to a single file...")
    f = open("data_enrichment/fmm_input/trips_ENVIROCAR.csv", "w+")
    f.write("id;geom\n")
    total_id = 0
    counter = 0
    total_id_arr = []
    total_df = pd.DataFrame()
    total_df.insert(0, "total_id", "")
    for root, dirs, files in os.walk("data_acquisition/envirocar_data/" + CITY + "/"):
        for dir in dirs:
            files = os.listdir(root + dir)
            for file in files:
                try:
                    # Read each file from a trip
                    df = pd.read_csv(root + dir + "/" + file, encoding="utf-8", sep=",")
                    assert (len(df) > 2)  # if the file does not contain valid information go to except statement
                    for i in range(len(df)):
                        total_id_arr.append(total_id)
                        total_id += 1
                    # df.to_csv("./data_enrichment/input/Bonn_Envirocar.csv")
                except:
                    print(f"Error reading file {file} in {dir}")
                    break

                total_df = pd.concat([total_df,df])
                total_df["total_id"] = total_id_arr
                # print(f"{dir} / {file} done'")
                # break
            # break
        # break
        total_df["total_id"] = total_id_arr
        total_df = total_df.loc[:, ~total_df.columns.str.contains('^Unnamed')]
        total_df.to_csv('data_acquisition/data/' + CITY + '/envirocar/' + CITY + "_ENVIROCAR.csv", mode="w+")


CITY = ""


def main_process(cities):
    global CITY
    # Setup configuration file
    confparser = configparser.RawConfigParser()
    configFilePath = r'config.ini'
    confparser.read(configFilePath)

    if not os.path.isdir('data_enrichment/input'):
        os.makedirs('data_enrichment/input')

    for CITY in cities:
        # Get BB of each city
        BB_string = confparser.get('BB-Config', CITY).replace(";", ",")  # lat1, long1, lat2, long2
        BB_arr = BB_string.split(",")

        # filter_data(BB_arr)

        BB = BB_arr[1] + "," + BB_arr[3] + "," + BB_arr[0] + "," + BB_arr[2]  # long1, long2, lat1, lat2 (FMM order)
        BB = [float(numeric_string) for numeric_string in BB.split(',')]  # Get BB
        TIME_START = confparser.get('main-config', 'TIME_START').replace('-', '')  # Get start time
        TIME_END = confparser.get('main-config', 'TIME_END').replace('-', '')  # Get end time

        collect_trips(BB)
        create_trip_file()


if __name__ == '__main__':
    cities = ["bonn", "koeln", "hamburg", "berlin", "muenster", "moenchengladbach", "duesseldorf", "muenchen",
              "stuttgart", "dortmund", "bremen", "chemnitz"]

    # Collects all available envirocar data
    # collect_data.main()

    # Processes the data for all defined cities
    main_process(cities)
