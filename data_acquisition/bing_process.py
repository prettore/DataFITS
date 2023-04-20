import logging
import os
import datetime
import pandas as pd
import json
import time

INPUT_DIR = "data_acquisition/data/"

#   Bing incident type
incidentTypeDic = {1: 'ACCIDENT', 2: "CONGESTION", 3: 'DISABLED VEHICLE', 4: 'MASS TRANSIT'
    , 5: 'MISCELLANEOUS', 6: 'OTHER NEWS', 7: 'PLANNED EVENT', 8: 'ROAD HAZARD'
    , 9: 'CONSTRUCTION', 10: 'Alert', 11: 'WEATHER'}

#   Bing incident severity
incidentSeverityDic = {1: 'LowImpact', 2: "Minor", 3: 'Moderate', 4: 'Serious'}


#   save traffic information to CSV file
def convert_incident_to_csv(Incident_Dir):
    #   convert all incident json files into a filtered CSVs
    for dirName, subdirList, fileList in os.walk(Incident_Dir):
        for fname in fileList:
            if fname.find(".txt") != -1:  # checking .txt
                incident_dict_csv = []
                with open(dirName + fname) as f:
                    for line in f:

                        try:
                            incident_line = json.loads(line)
                            # print incident_line

                            if (incident_line["authenticationResultCode"] == 'ValidCredentials') and len(incident_line[
                                                                                                             "resourceSets"]) > 0:  # Authentication successful and resourceSets not empty

                                incident_comments = None

                                for i in range(len(incident_line["resourceSets"][0]["resources"])):

                                    incident_id = (incident_line["resourceSets"][0]["resources"][i]["incidentId"])
                                    incident_verified = (incident_line["resourceSets"][0]["resources"][i]["verified"])

                                    incident_type = incidentTypeDic[
                                        incident_line["resourceSets"][0]["resources"][i]["type"]]

                                    incident_start_time = pd.to_datetime(
                                        int(str(incident_line["resourceSets"][0]["resources"][i]["start"])
                                            .replace("/Date(", "").replace(")/", "")), unit='ms')
                                    incident_end_time = pd.to_datetime(
                                        int(str(incident_line["resourceSets"][0]["resources"][i]["end"])
                                            .replace("/Date(", "").replace(")/", "")), unit='ms')
                                    incident_last_modified = pd.to_datetime(
                                        int(str(incident_line["resourceSets"][0]["resources"][i]["lastModified"])
                                            .replace("/Date(", "").replace(")/", "")), unit='ms')

                                    incident_criticality = incidentSeverityDic[
                                        incident_line["resourceSets"][0]["resources"][i]["severity"]]

                                    incident_road_closed = (
                                        incident_line["resourceSets"][0]["resources"][i]["roadClosed"])

                                    if "description" in incident_line["resourceSets"][0]["resources"][i]:
                                        incident_comments = str(
                                            incident_line["resourceSets"][0]["resources"][i]["description"])

                                    incident_lat_from = (
                                        incident_line["resourceSets"][0]["resources"][i]["point"]["coordinates"][0])
                                    incident_long_from = (
                                        incident_line["resourceSets"][0]["resources"][i]["point"]["coordinates"][1])

                                    incident_lat_to = (
                                        incident_line["resourceSets"][0]["resources"][i]["toPoint"]["coordinates"][0])
                                    incident_long_to = (
                                        incident_line["resourceSets"][0]["resources"][i]["toPoint"]["coordinates"][1])

                                    # formatting the data in order to after save it as CSV
                                    incident_dict_csv.append({"incident_id": incident_id,
                                                              "incident_verified": incident_verified,
                                                              "incident_type": incident_type,
                                                              "incident_road_closed": incident_road_closed,
                                                              "incident_start_time": incident_start_time,
                                                              "incident_end_time": incident_end_time,
                                                              "incident_last_modified": incident_last_modified,
                                                              "incident_criticality": incident_criticality,
                                                              "incident_comments": incident_comments,
                                                              "incident_lat_from": incident_lat_from,
                                                              "incident_long_from": incident_long_from,
                                                              "incident_lat_to": incident_lat_to,
                                                              "incident_long_to": incident_long_to})
                        except Exception as e:
                            logging.error(e)
                            print("Oops!  That was no valid traffic data.  Trying next one...")

                if len(incident_dict_csv) != 0:
                    # # save json
                    # fullTrafficDic = ({"type": "FeatureCollection", "features": trafficDicGJ})
                    # with open(folderTraffic+trafficFile.replace(".text","")+"(Traffic).json", 'w') as outfile:
                    #     json.dump(fullTrafficDic, outfile)
                    # save csv
                    try:
                        df_traffic = pd.DataFrame(incident_dict_csv, columns=("incident_id", "incident_verified",
                                                                              "incident_type", "incident_road_closed",
                                                                              "incident_start_time",
                                                                              "incident_end_time",
                                                                              "incident_last_modified",
                                                                              "incident_criticality",
                                                                              "incident_comments", "incident_lat_from",
                                                                              "incident_long_from", "incident_lat_to",
                                                                              "incident_long_to"))

                        timestr = datetime.datetime.utcnow().strftime("%Y%m%d")

                        if not os.path.isfile(dirName + fname.replace(".txt", "") + timestr + ".csv"):
                            header_val = True
                            write_mode = "w+"
                        else:
                            header_val = False
                            write_mode = "a"

                        df_traffic.to_csv(dirName + fname.replace(".txt", "") + timestr + ".csv", sep=",", index=False,
                                          mode=write_mode, header=header_val, encoding="utf-8")

                        # df_traffic.to_csv(dirName + fname.replace(".txt","") + ".csv", sep=",", index=False)
                        logging.info("BING_Incident: Converted csv file for " + str(dirName))
                    except Exception as x:
                        logging.error("Error creating the BING_Incident csv file for " + str(dirName))
                        logging.error(x)


#   join CSV files and remove the individual ones
def join_csv_files(folder, remove_original):
    for dirName, subdirList, fileList in os.walk(folder):
        try:
            df_final = pd.DataFrame()
            # print('Found directory: %s' % dirName)
            for fname in fileList:
                if fname.find(".csv") != -1:  # checking .csv
                    df_final = df_final.append(pd.read_csv(dirName + fname, index_col=0))  # , sort=False)
                    if remove_original == True:
                        os.remove(dirName + fname)

            # df_final.to_csv(dirName + dirName.split("/")[0] + "_" + dirName.split("/")[1] + ".csv", sep=",")

            df_final.to_csv(dirName + dirName.split("/")[1] + "_Incident_BING.csv", sep=",", mode="a")
            logging.info("BING_Incident: Joined csv file for " + str(dirName))
        except Exception as x:
            logging.error("Error joining the BING_Incident csv files for " + str(dirName))
            logging.error(x)


#   remove all incident json files
def remove_txt_files(folder):
    for dirName, subdirList, fileList in os.walk(folder):
        # print('Found directory: %s' % dirName)
        for fname in fileList:
            if fname.find(".txt") != -1:  # checking .txt
                os.remove(dirName + fname)


def main(city_list, time, logging_lvl):
    # threading.Timer((time*60), main, [city_list, time, logging_lvl]).start()

    logging.basicConfig(filename='logfile.log', level=logging_lvl, format='%(asctime)s, %(levelname)s %(message)s',
                        datefmt='%Y-%m-%d,%H:%M:%S')

    #   convert all incident json files into a filtered CSVs
    for dir_name, subdir_list, file_list in os.walk(INPUT_DIR):
        # print('Found directory: %s' % dir_name)
        for subdir in subdir_list:
            if subdir in city_list:
                for dirs, subdirs, files in os.walk(INPUT_DIR + subdir + "/Incident_BING/"):
                    #   convert all incident json files in filtered CSVs
                    convert_incident_to_csv(dirs)

    #   remove all incident json files
    for dir_name, subdir_list, file_list in os.walk(INPUT_DIR):
        # print('Found directory: %s' % dir_name)
        for subdir in subdir_list:
            if subdir in city_list:
                for dirs, subdirs, files in os.walk(INPUT_DIR + subdir + "/Incident_BING/"):
                    remove_txt_files(dirs)
                    pass

    return True
