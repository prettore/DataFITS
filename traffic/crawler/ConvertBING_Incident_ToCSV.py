import logging
import os
import datetime
import pandas as pd
import json
import time

INPUT_DIR_INCIDENT = "./"

#   Bing incident type
incidentTypeDic = {1: 'ACCIDENT', 2: "CONGESTION", 3: 'DISABLED VEHICLE', 4: 'MASS TRANSIT'
    , 5: 'MISCELLANEOUS', 6: 'OTHER NEWS', 7: 'PLANNED EVENT', 8: 'ROAD HAZARD'
    , 9: 'CONSTRUCTION', 10: 'Alert', 11: 'WEATHER'}

#   Bing incident severity
incidentSeverityDic = {1: 'LowImpact', 2: "Minor", 3: 'Moderate', 4: 'Serious'}


#   save traffic information to CSV file
def convertIncident2CSV(Incident_Dir):
    #   convert all incident json files into a filtered CSVs
    for dirName, subdirList, fileList in os.walk(Incident_Dir):
        #print('Found directory: %s' % dirName)
        for fname in fileList:
            if (fname.find(".txt") != -1):  # checking .txt

                incidentDicCSV = []
                with open(dirName + fname) as f:
                    for line in f:

                        try:
                            incidentLine = json.loads(line)
                            # print incidentLine

                            if (incidentLine["authenticationResultCode"] == 'ValidCredentials') and len(incidentLine["resourceSets"]) > 0:  # Authentication successful and resourceSets not empty

                                incidentComments = None

                                for i in range(len(incidentLine["resourceSets"][0]["resources"])):

                                    incidentID = (incidentLine["resourceSets"][0]["resources"][i]["incidentId"])
                                    incidentVerified = (incidentLine["resourceSets"][0]["resources"][i]["verified"])

                                    incidentType = incidentTypeDic[incidentLine["resourceSets"][0]["resources"][i]["type"]]


                                    incidentStartTime = pd.to_datetime(int(str(incidentLine["resourceSets"][0]["resources"][i]["start"])
                                                                           .replace("/Date(","").replace(")/","")),unit='ms')
                                    incidentEndTime = pd.to_datetime(int(str(incidentLine["resourceSets"][0]["resources"][i]["end"])
                                                                         .replace("/Date(","").replace(")/","")),unit='ms')
                                    incidentLastModified = pd.to_datetime(int(str(incidentLine["resourceSets"][0]["resources"][i]["lastModified"])
                                                                              .replace("/Date(","").replace(")/","")),unit='ms')

                                    incidentCriticality = incidentSeverityDic[incidentLine["resourceSets"][0]["resources"][i]["severity"]]

                                    incidentRoadClosed = (
                                        incidentLine["resourceSets"][0]["resources"][i]["roadClosed"])

                                    if ("description" in incidentLine["resourceSets"][0]["resources"][i]):
                                        incidentComments = str(incidentLine["resourceSets"][0]["resources"][i]["description"])

                                    incidentLat_From = (incidentLine["resourceSets"][0]["resources"][i]["point"]["coordinates"][0])
                                    incidentLong_From = (incidentLine["resourceSets"][0]["resources"][i]["point"]["coordinates"][1])

                                    incidentLat_To = (incidentLine["resourceSets"][0]["resources"][i]["toPoint"]["coordinates"][0])
                                    incidentLong_To = (incidentLine["resourceSets"][0]["resources"][i]["toPoint"]["coordinates"][1])

                                                                        # formatting the data in order to after save it as CSV
                                    incidentDicCSV.append({"incidentID": incidentID,
                                                           "incidentVerified": incidentVerified,
                                                           "incidentType": incidentType,
                                                           "incidentRoadClosed": incidentRoadClosed,
                                                           "incidentStartTime": incidentStartTime,
                                                           "incidentEndTime": incidentEndTime,
                                                           "incidentLastModified": incidentLastModified,
                                                           "incidentCriticality": incidentCriticality,
                                                           "incidentComments": incidentComments,
                                                           "incidentLat_From": incidentLat_From,
                                                           "incidentLong_From": incidentLong_From,
                                                           "incidentLat_To": incidentLat_To,
                                                           "incidentLong_To": incidentLong_To})


                        except Exception as e:
                            logging.error(e)
                            print("Oops!  That was no valid traffic data.  Trying next one...")

                if (len(incidentDicCSV) != 0):
                    # # save json
                    # fullTrafficDic = ({"type": "FeatureCollection", "features": trafficDicGJ})
                    # with open(folderTraffic+trafficFile.replace(".text","")+"(Traffic).json", 'w') as outfile:
                    #     json.dump(fullTrafficDic, outfile)
                    # save csv
                    try:
                        df_Traffic = pd.DataFrame(incidentDicCSV, columns=("incidentID", "incidentVerified",
                                                                        "incidentType", "incidentRoadClosed",
                                                                        "incidentStartTime", "incidentEndTime",
                                                                        "incidentLastModified", "incidentCriticality",
                                                                        "incidentComments", "incidentLat_From",
                                                                        "incidentLong_From", "incidentLat_To",
                                                                        "incidentLong_To"))

                        timestr = datetime.datetime.utcnow().strftime("%Y%m%d")

                        if not os.path.isfile(dirName + fname.replace(".txt","") +timestr+ ".csv"):
                            HEADER_VAL = True
                            WRITE_MODE = "w+"
                        else:
                            HEADER_VAL = False
                            WRITE_MODE = "a"

                        df_Traffic.to_csv(dirName + fname.replace(".txt","") + timestr + ".csv", sep=",", index=False, mode = WRITE_MODE, header = HEADER_VAL, encoding="utf-8")
                        
                        #df_Traffic.to_csv(dirName + fname.replace(".txt","") + ".csv", sep=",", index=False)
                        logging.info("BING_Incident: Converted csv file for "+str(dirName))
                    except Exception as x:
                        logging.error("Error creating the BING_Incident csv file for "+str(dirName))
                        logging.error(x)


#   join CSV files and remove the individual ones
def joinCSVFiles(FOLDER, RemoveOriginal):
    for dirName, subdirList, fileList in os.walk(FOLDER):
        try:
            df_final = pd.DataFrame()
            #print('Found directory: %s' % dirName)
            for fname in fileList:
                if (fname.find(".csv") != -1):  # checking .csv
                    # df_final = pd.DataFrame(
                    #     {{fname: pd.read_csv(dirName + fname).iat[-1, 1] for fname in fileList if (fname.find(".csv") != -1)}})
                    df_final = df_final.append(pd.read_csv(dirName + fname, index_col=0))#, sort=False)
                    if (RemoveOriginal == True):
                        os.remove(dirName + fname)

            #df_final.to_csv(dirName + dirName.split("/")[0] + "_" + dirName.split("/")[1] + ".csv", sep=",")

            df_final.to_csv(dirName + dirName.split("/")[1] + "_Incident_BING.csv", sep=",", mode="a")
            logging.info("BING_Incident: Joined csv file for "+str(dirName))
        except Exception as x:
            logging.error("Error joining the BING_Incident csv files for "+str(dirName))
            logging.error(x)

#   remove all incident json files
def removeTXTFiles(FOLDER):
    for dirName, subdirList, fileList in os.walk(FOLDER):
        #print('Found directory: %s' % dirName)
        for fname in fileList:
            if (fname.find(".txt") != -1):  # checking .txt
                    os.remove(dirName + fname)


def main(city_list, time, logging_lvl):
    #threading.Timer((time*60), main, [city_list, time, logging_lvl]).start()

    logging.basicConfig(filename='logfile.log', level=logging_lvl, format='%(asctime)s, %(levelname)s %(message)s',datefmt='%Y-%m-%d,%H:%M:%S')

    #   convert all incident json files into a filtered CSVs
    for dirName, subdirList, fileList in os.walk(INPUT_DIR_INCIDENT):
        #print('Found directory: %s' % dirName)
        for subdir in subdirList:
            if subdir in city_list:
                for dirName, subdirList, fileList in os.walk(INPUT_DIR_INCIDENT+subdir+"/IncidentBING/"):
                    #print('Found subdirectory: %s' % dirName)

                    #   convert all incident json files in filtered CSVs
                    convertIncident2CSV(dirName)

                    #   join CSV files and remove the individual ones
                    #joinCSVFiles(dirName,True)



    #   remove all incident json files
    for dirName, subdirList, fileList in os.walk(INPUT_DIR_INCIDENT):
        # print('Found directory: %s' % dirName)
        for subdir in subdirList:
            if subdir in city_list:
                for dirName, subdirList, fileList in os.walk(INPUT_DIR_INCIDENT + subdir + "/IncidentBING/"):
                    removeTXTFiles(dirName)
                    pass

    return True