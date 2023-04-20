import json
from geojson import Feature, MultiLineString, LineString, Point
from geojson.feature import FeatureCollection
import re
import pandas as pd
import os
import configparser
from tqdm import tqdm  # for the progress bar
import pathlib
import time

"""
This script combines the fmm output with the fused data
"""

def create_json_output(df, SOURCE):
    """
    Creates a geojson output of the fused dataset
    """
    features = []

    f = open("fmm_output/output_" + SOURCE + ".csv", "r")
    next(f)

    wrongEntry_IDs = []

    for line in f.readlines():
        line = line.split("LINESTRING")[1]
        cords = []
        cords = re.findall(r'\d+[.,]\d*', line)
        cords = [float(i) for i in cords]
        str_elem = []
        for i in range(0, len(cords) - 1, 2):
            str_elem += ([[cords[i], cords[i + 1]]])
        str_elem = LineString(str_elem)
        features.append(Feature(geometry=str_elem, properties={"id": id}))
    return
    # print("Trying to create feature collection")
    feature_collection = FeatureCollection(features)
    # print("FeatureCollection created")

    # Export the geojson file to the output destination
    with open("geojson_output/" + "geojson_" + SOURCE + ".json", "w+") as f:  # geojson_file_name[SOURCE],"w+") as f:
        json.dump(feature_collection, f)
    print("json exported")


def create_csv_output(df, SOURCE):
    print("Creating json and csv output...")
    global CNT_trafficOD, CNT_trafficHERE
    features = []
    feature_collection = []
    counter = 0

    ids = []
    opath_arr = []
    cpath_arr = []
    csv_cords = []
    origin_ids = []

    od_id_name = {
        "Koeln": "ID",
        "Bonn": "Road Id",
    }

    input_df = pd.read_csv("fmm_output/output_" + SOURCE + ".csv", sep=";")
    input_df = input_df.sort_values(by=["id"])
    input_df.to_csv("fmm_output/output_" + SOURCE + ".csv", sep=";", index=False)

    f = open("fmm_output/output_" + SOURCE + ".csv", "r")
    next(f)

    wrongEntry_IDs = []

    for line in tqdm(f.readlines()):
        id = int(line.split(";")[0])  # gets the id value of the entry
        opath = line.split(";")[1]
        cpath = line.split(";")[2]  # gets the cpath values of the entry
        if len(cpath) == 0:  # if there is no cpath or cpath value, there was a problem in the fmm process
            print(f"!! ERROR in line {counter} with the following content: {line[:-1]} !!")
            cpath = "-1"
            wrongEntry_IDs.append(counter)  # add the ID of the problematic entry, to later drop it
            counter += 1
            continue
            # Then there is no matched road
        line = line.split("LINESTRING")[1]
        cords = []
        cords = re.findall(r'\d+[.,]\d*', line)
        cords = [float(i) for i in cords]
        # Create geojson
        str_elem = []
        point = False
        for i in range(0, len(cords) - 1, 2):
            if SOURCE == ("CONSTRUCTION_OD") or (SOURCE == "Envirocar"):
                str_elem += ([cords[i], cords[i + 1]])
                point = True
                break
            else:
                str_elem += ([[cords[i], cords[i + 1]]])
        if point:
            str_elem = Point(str_elem)
        else:
            str_elem = LineString(str_elem)
        features.append(Feature(geometry=str_elem, properties={"id": id}))
        feature_collection = FeatureCollection(features)

        ids.append(id)  # add the id of the value to a new id array
        opath_arr.append(list(set([int(opath_val) for opath_val in opath.split(
            ",")])))  # add the numeric values to a new array and remove double entries
        cpath_arr.append(list(set([int(cpath_val) for cpath_val in cpath.split(
            ",")])))  # add the numeric values to a new array and remove double entries
        csv_cords.append(str_elem)
        origin_ids.append(id)

        counter += 1

    information = pd.DataFrame({"id": ids, "opath": opath_arr, "cpath": cpath_arr, "coords": csv_cords})
    # sort the data by id
    information = information.sort_values(by=["id"])

    # Export the geojson file to the output destination
    with open("geojson_output/" + "geojson_" + SOURCE + ".json", "w+") as f:  # geojson_file_name[SOURCE],"w+") as f:
        json.dump(feature_collection, f)

    # All entries that could not be matched by fmm are dropped
    for entry in wrongEntry_IDs:
        print(f"{SOURCE} dropped entry with ID {entry}")
        df = df.drop(index=entry)
        if SOURCE == "TRAFFIC_OD":
            CNT_trafficOD -= 1
        elif SOURCE == "TRAFFIC_HERE":
            CNT_trafficHERE -= 1
    df = df.reset_index(drop=True)
    traff_here_ids = {}
    traff_od_ids = {}
    if SOURCE == "TRAFFIC_HERE":
        for i in range(CNT_trafficHERE):
            traff_here_ids[(df["streetIntersection"][i], df["streetName"][i], df["streetDirection"][i])] = i
        # print(traff_here_ids)

    if "TRAFFIC" in SOURCE:
        opath_arr_1 = information["opath"]  # opath_arr
        cpath_arr_1 = information["cpath"]  # cpath_arr
        csv_cords_1 = information["id"]  # csv_cords
        opath_arr = []
        cpath_arr = []
        csv_cords = []
        origin_ids = []
        wrong_entries = 0
        print("Preprocessing Traffic Data")
        df_len = df.shape[0]
        start = time.time()
        key_error_cnt = 0
        for index, row in df.iterrows():
            if SOURCE == "TRAFFIC_HERE":
                # row["id"] = index
                # if [row["streetID"],row["streetIntersection"]] == traff_here_ids[index%CNT_trafficHERE]:
                # cpath_arr.append(cpath_arr_1[index%CNT_trafficHERE])
                # csv_cords.append(csv_cords_1[index%CNT_trafficHERE])
                # else:
                try:
                    # if [row["streetID"],row["streetIntersection"]] in traff_here_ids:
                    idx = traff_here_ids[(df["streetIntersection"].iloc[index], df["streetName"].iloc[index],
                                          df["streetDirection"].iloc[index])]
                    # idx = traff_here_ids.index([row["streetID"],row["streetIntersection"]])
                    opath_arr.append(opath_arr_1[idx])
                    cpath_arr.append(cpath_arr_1[idx])
                    csv_cords.append(csv_cords_1[idx])
                    origin_ids.append(ids[idx])
                except KeyError:
                    key_error_cnt += 1
                    opath_arr.append(None)
                    cpath_arr.append(None)
                    csv_cords.append(None)
                    origin_ids.append(None)
                    # df = df.drop(df.index[index])
                    # Alternative: Set cpath to NONE and drop all NONE rows
            if SOURCE == "TRAFFIC_OD":
                for i in range(CNT_trafficOD):
                    traff_od_ids[df[od_id_name[CITY]][i]] = i
                # row["id"] = index
                try:
                    idx = traff_od_ids[df[od_id_name[CITY]].iloc[index]]
                    opath_arr.append(opath_arr_1[idx])
                    cpath_arr.append(cpath_arr_1[idx])
                    csv_cords.append(csv_cords_1[idx])
                    origin_ids.append(ids[idx])
                except KeyError:
                    key_error_cnt += 1
                    opath_arr.append(None)
                    cpath_arr.append(None)
                    csv_cords.append(None)
                    origin_ids.append(None)

            print(f"Processed {index} / {df_len}", end='\r')
        print(f"Processed {index} / {df_len}")
        print(f"The dataset contained {key_error_cnt} entries with no matching keys")

        if SOURCE == "TRAFFIC_HERE":
            # Drop the 3 columns as they are not that important but take a lot of space and processing power
            df = df.drop(['streetIntersectionSHP'], axis=1)
            df = df.drop(['streetID'], axis=1)
            df = df.drop(['streetIntersection'], axis=1)
        end = time.time()
        print(f"TIME {end - start}")
    df["origin_ids"] = origin_ids
    df["opath"] = opath_arr
    df["cpath"] = cpath_arr
    df["new_cords"] = csv_cords
    # Drop rows containing None values
    df = df[df["cpath"].notna()]
    try:
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    except:
        pass

    # Rename Timestamp column (this is already done in preparation.py, but if the user did not prepare the data
    # before its done here again)
    try:
        df = df.rename(columns={configparser.get('Timestamp-Config', SOURCE.lower()): "Time"})
    except:
        pass  # already named correctly
    df.to_csv("output/test_" + SOURCE + ".csv")


# Setup config file
configparser = configparser.RawConfigParser()
configFilePath = r'../config.ini'
configparser.read(configFilePath)

# Create geojson output and total output folder
pathlib.Path("./geojson_output").mkdir(parents=True, exist_ok=True)
pathlib.Path("./output").mkdir(parents=True, exist_ok=True)

Sources = configparser.options("Sources")
CITY = configparser.get('main-config', 'CITY')

# The number of single different roads
CNT_trafficHERE = int(configparser.get('Data-Config', 'CNT_traffic_HERE'))
CNT_trafficOD = int(configparser.get('Data-Config', 'CNT_traffic_OD'))

cwd = os.getcwd()
crr_dir = cwd + "/"

for root, dirs, files in os.walk(crr_dir + "/input/"):
    for file in files:
        if file.startswith("."):
            continue  # ignore hidden files
        for src in Sources:
            if src in file.lower() and CITY.lower() in file.lower():
                SOURCE = src.upper()
                print(f"Creating {SOURCE}")
                if SOURCE == "ADAC":
                    print("ADAC is not implemented yet")
                    break
                fmm_input = pd.read_csv(crr_dir + "fmm_input/trips_" + SOURCE + ".csv", sep=";")
                length = fmm_input.shape[0]
                print(f'-- Loaded {length} matched trajectories')
                df = pd.read_csv(crr_dir + "input/" + CITY + "_" + SOURCE + ".csv")
                print(f'-- Loaded {df.shape[0]} input entries')
                # df = pd.read_csv(crr_dir+"trips_INCIDENT_BING.csv", sep=";")
                create_csv_output(df, SOURCE)
                print(f"--> {SOURCE} completed")
