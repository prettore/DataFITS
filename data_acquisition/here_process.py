import logging
import os
from datetime import datetime
import pandas as pd
import json
import time

INPUT_DIR = "data_acquisition/data/"

#   Here incident criticality
incidentCriticalityDic = {3: 'LowImpact', 2: "Minor", 1: 'Moderate', 0: 'Serious'}


#   calculating the lat long average
def mean_of_coordinates(shp):
    lat = 0
    long = 0
    count = 0
    for coord in str(shp).split(' '):
        if coord != "":
            lat = lat + float(coord.split(',')[0])
            long = long + float(coord.split(',')[1])
            count = count + 1

    lat = lat / count
    long = long / count

    return long, lat


#   invert lat long order
def invert_coordinates(shp):
    lat = []
    long = []
    # coord = []
    for coord in str(shp).split(' '):
        if coord != "":
            lat.append(float(coord.split(',')[0]))
            long.append(float(coord.split(',')[1]))

    # coord = []
    json_street_coord = '['
    for i in range(0, len(lat)):
        # coord.append((long[i],lat[i]))
        if (i != (len(lat) - 1)):
            json_street_coord = json_street_coord + '{"lat":''"' + str(lat[i]) + '",' + '"long":"' + str(
                long[i]) + '"},'
        else:
            json_street_coord = json_street_coord + '{"lat":''"' + str(lat[i]) + '",' + '"long":"' + str(long[i]) + '"}'

    json_street_coord = json_street_coord + ']'

    # json format streetCoord
    # {"streetSeg": [
    #     {"lat": "number", "long": "number"},
    #     {"lat": "number", "long": "number"},
    #     {"lat": "number", "long": "number"}
    # ],
    # [
    #     {"lat": "number", "long": "number"},
    #     {"lat": "number", "long": "number"},
    #     {"lat": "number", "long": "number"}
    # ]
    # }

    return json_street_coord


#   extract traffic information from HERE json file
def current_flow_long_street(trafficInformation):
    CN = trafficInformation["CN"]
    JF = trafficInformation["JF"]
    FF = trafficInformation["FF"]
    sp = None
    su = None

    if "SSS" in trafficInformation:
        sp_max = 0
        su_max = 0
        for k in range(len(trafficInformation["SSS"]["SS"])):

            sp = trafficInformation["SSS"]["SS"][k]["SP"]

            if sp_max < sp:
                sp_max = sp
            if "su" in trafficInformation["SSS"]["SS"][k]:
                su = trafficInformation["SSS"]["SS"][k]["SU"]
                if su_max < su:
                    su_max = su
    else:
        sp = trafficInformation["SP"]
        if "su" in trafficInformation:
            su = trafficInformation["SU"]

    # print("Distance: " + str(minDistanceKm) + " of " + minIntersectionName +
    #       " CN: "+str(CN)+" JF: "+str(JF)+" FF: "+str(FF)+" sp: "+str(sp)+" su: "+str(su))
    return CN, JF, FF, sp, su


#   save traffic information to CSV file
def convert_traffic_to_csv(Traffic_Dir):
    #   convert all traffic json files into a filtered CSVs
    for dirName, subdirList, fileList in os.walk(Traffic_Dir):
        for fname in fileList:
            if fname.find(".txt") != -1:  # checking .txt
                trafficDicCSV = []
                trafficDicGJ = []
                with open(dirName + fname) as f:
                    for line in f:
                        try:
                            trafficLine = json.loads(line)
                            if len(trafficLine) > 2:  # means that there is no Authentication Error
                                for i in range(len(trafficLine["RWS"][0]["RW"])):
                                    createdTimestamp = str(trafficLine["CREATED_TIMESTAMP"])
                                    nokiaID = str(trafficLine["RWS"][0]["RW"][i]["mid"])
                                    street = trafficLine["RWS"][0]["RW"][i]["DE"]  # .encode('utf-8')
                                    for j in range(len(trafficLine["RWS"][0]["RW"][i]["FIS"][0]["FI"])):
                                        streetIntersection = None
                                        streetCoord = []
                                        FC = []
                                        streetDirection = None
                                        jsonStreetCoord = '{"streetSeg": ['
                                        currentFlow = current_flow_long_street(
                                            trafficLine["RWS"][0]["RW"][i]["FIS"][0]["FI"][j]["CF"][0])
                                        if "DE" in trafficLine["RWS"][0]["RW"][i]["FIS"][0]["FI"][j]["TMC"]:
                                            streetIntersection = \
                                                trafficLine["RWS"][0]["RW"][i]["FIS"][0]["FI"][j]["TMC"][
                                                    "DE"]  # .encode('utf-8')
                                        for w in range(len(trafficLine["RWS"][0]["RW"][i]["FIS"][0]["FI"][j]["SHP"])):
                                            # streetCoord.append(invertCoordinates(trafficLine["RWS"][0]["RW"][i]["FIS"][0]["FI"][j]["SHP"][w]["value"][0]))
                                            if (w != (
                                                    len(trafficLine["RWS"][0]["RW"][i]["FIS"][0]["FI"][j]["SHP"]) - 1)):
                                                jsonStreetCoord = jsonStreetCoord + invert_coordinates(
                                                    trafficLine["RWS"][0]["RW"][i]["FIS"][0]["FI"][j]["SHP"][w][
                                                        "value"][0]) + ","
                                            else:
                                                jsonStreetCoord = jsonStreetCoord + invert_coordinates(
                                                    trafficLine["RWS"][0]["RW"][i]["FIS"][0]["FI"][j]["SHP"][w][
                                                        "value"][0])

                                            # streetCoord.append(meanOfCoordinates(str(trafficLine["RWS"][0]["RW"][i]["FIS"][0]["FI"][j]["SHP"][w]["value"][0])))
                                            FC.append(trafficLine["RWS"][0]["RW"][i]["FIS"][0]["FI"][j]["SHP"][w]["FC"])

                                        jsonStreetCoord = jsonStreetCoord + "]}"
                                        streetCoord.append(jsonStreetCoord)
                                        if "QD" in trafficLine["RWS"][0]["RW"][i]["FIS"][0]["FI"][j]["TMC"]:
                                            streetDirection = trafficLine["RWS"][0]["RW"][i]["FIS"][0]["FI"][j]["TMC"][
                                                "QD"]  # .encode('utf-8')

                                        if len(streetCoord) == 1:
                                            streetCoord = streetCoord[0]
                                            # geometryType = "Point"
                                            geometryType = "LineString"

                                        else:
                                            geometryType = "MultiLineString"

                                        # formatting the data in order to after save it as CSV
                                        trafficDicCSV.append({"createdTimestamp": createdTimestamp, "streetID": nokiaID,
                                                              "streetName": street,
                                                              "streetIntersection": streetIntersection,
                                                              "streetDirection": streetDirection,
                                                              "streetIntersectionSHP": streetCoord, "FC": FC,
                                                              "CN": currentFlow[0],
                                                              "JF": currentFlow[1], "FF": currentFlow[2],
                                                              "SP": currentFlow[3],
                                                              "SU": currentFlow[4]})

                                        # formatting the data in order to after save it as GeoJson
                                        trafficDicGJ.append({
                                            "type": "Feature",
                                            "geometry": {
                                                "type": geometryType,
                                                "coordinates": streetCoord
                                            },
                                            "properties": {
                                                "createdTimestamp": createdTimestamp,
                                                "streetID": nokiaID,
                                                "streetName": street,
                                                "streetIntersection": streetIntersection,
                                                "streetDirection": streetDirection,
                                                "FC": FC,
                                                "CN": currentFlow[0],
                                                "JF": currentFlow[1],
                                                "FF": currentFlow[2],
                                                "SP": currentFlow[3],
                                                "SU": currentFlow[4]
                                            }
                                        }, )
                        except ValueError:
                            print("Oops!  That was no valid traffic data.  Trying next one...")

                if len(trafficDicCSV) != 0:
                    # # save json
                    # fullTrafficDic = ({"type": "FeatureCollection", "features": trafficDicGJ})
                    # with open(folderTraffic+trafficFile.replace(".text","")+"(Traffic).json", 'w') as outfile:
                    #     json.dump(fullTrafficDic, outfile)
                    # save csv

                    timestr = datetime.utcnow().strftime("%Y%m%d")
                    try:
                        df_Traffic = pd.DataFrame(trafficDicCSV, columns=(
                            "createdTimestamp", "streetID", "streetName", "streetIntersection", "streetDirection",
                            "streetIntersectionSHP",
                            "FC", "CN", "JF", "FF", "SP", "SU"))

                        if not os.path.isfile(dirName + fname.replace(".txt", "") + timestr + ".csv"):
                            HEADER_VAL = True
                            WRITE_MODE = "w+"
                        else:
                            HEADER_VAL = False
                            WRITE_MODE = "a"

                        df_Traffic.to_csv(dirName + fname.replace(".txt", "") + timestr + ".csv", index=False,
                                          mode=WRITE_MODE, header=HEADER_VAL, encoding="utf-8")
                        # df_Traffic.to_csv(dirName + fname.replace(".txt","")+".csv", sep=",", index=False)

                        logging.info("HERE_Traffic: Converted csv file for " + str(dirName))
                    except Exception as x:
                        logging.error("Error creating the HERE_Traffic csv file for " + str(dirName))
                        logging.error(x)


#   save traffic information to CSV file
def convert_incident_to_csv(Incident_Dir):
    #   convert all incident json files into a filtered CSVs
    for dirName, subdirList, fileList in os.walk(Incident_Dir):
        # print('Found directory: %s' % dirName)
        for fname in fileList:
            if fname.find(".txt") != -1:  # checking .txt

                incidentDicCSV = []
                with open(dirName + fname) as f:
                    for line in f:

                        try:
                            incidentLine = json.loads(line)
                            # print incidentLine

                            if len(incidentLine) > 2:  # true when there is no authentication error

                                incidentComments = None

                                createdTimestamp = datetime.strptime(str(incidentLine["TIMESTAMP"]),
                                                                     '%m/%d/%Y %H:%M:%S %Z')

                                for i in range(len(incidentLine["TRAFFICITEMS"]["TRAFFICITEM"])):
                                    incidentID = (incidentLine["TRAFFICITEMS"]["TRAFFICITEM"][i]["TRAFFICITEMID"])
                                    incidentVerified = (incidentLine["TRAFFICITEMS"]["TRAFFICITEM"][i]["VERIFIED"])

                                    incidentType = str(
                                        incidentLine["TRAFFICITEMS"]["TRAFFICITEM"][i]["TRAFFICITEMTYPEDESC"])

                                    incidentStartTime = datetime.strptime(
                                        str(incidentLine["TRAFFICITEMS"]["TRAFFICITEM"][i]["STARTTIME"]),
                                        '%m/%d/%Y %H:%M:%S')

                                    incidentEndTime = datetime.strptime(
                                        str(incidentLine["TRAFFICITEMS"]["TRAFFICITEM"][i]["ENDTIME"]),
                                        '%m/%d/%Y %H:%M:%S')
                                    incidentEntryTime = datetime.strptime(
                                        str(incidentLine["TRAFFICITEMS"]["TRAFFICITEM"][i]["ENTRYTIME"]),
                                        '%m/%d/%Y %H:%M:%S')

                                    incidentCriticality = incidentCriticalityDic[
                                        int(incidentLine["TRAFFICITEMS"]["TRAFFICITEM"][i]["CRITICALITY"]["ID"])]

                                    incidentRoadClosed = (
                                        incidentLine["TRAFFICITEMS"]["TRAFFICITEM"][i]["TRAFFICITEMDETAIL"][
                                            "ROADCLOSED"])

                                    if "COMMENTS" in incidentLine["TRAFFICITEMS"]["TRAFFICITEM"]:
                                        incidentComments = str(
                                            incidentLine["TRAFFICITEMS"]["TRAFFICITEM"][i]["COMMENTS"])

                                    incidentLat_From = (
                                        incidentLine["TRAFFICITEMS"]["TRAFFICITEM"][i]["LOCATION"]["GEOLOC"]["ORIGIN"][
                                            "LATITUDE"])
                                    incidentLong_From = (
                                        incidentLine["TRAFFICITEMS"]["TRAFFICITEM"][i]["LOCATION"]["GEOLOC"]["ORIGIN"][
                                            "LONGITUDE"])

                                    incidentLat_To = (
                                        incidentLine["TRAFFICITEMS"]["TRAFFICITEM"][i]["LOCATION"]["GEOLOC"]["TO"][0][
                                            "LATITUDE"])
                                    incidentLong_To = (
                                        incidentLine["TRAFFICITEMS"]["TRAFFICITEM"][i]["LOCATION"]["GEOLOC"]["TO"][0][
                                            "LONGITUDE"])

                                    if "DEFINED" in incidentLine["TRAFFICITEMS"]["TRAFFICITEM"][i]["LOCATION"]:
                                        incidentRoadway_From = (
                                            incidentLine["TRAFFICITEMS"]["TRAFFICITEM"][i]["LOCATION"]["DEFINED"][
                                                "ORIGIN"][
                                                "ROADWAY"]["DESCRIPTION"][0]["content"])
                                        incidentRoadway_To = (
                                            incidentLine["TRAFFICITEMS"]["TRAFFICITEM"][i]["LOCATION"]["DEFINED"]["TO"][
                                                "ROADWAY"]["DESCRIPTION"][0]["content"])
                                    else:
                                        incidentRoadway_From = ""
                                        incidentRoadway_To = ""

                                    # formatting the data in order to after save it as CSV
                                    incidentDicCSV.append({"Timestamp": createdTimestamp, "incidentID": incidentID,
                                                           "incidentVerified": incidentVerified,
                                                           "incidentType": incidentType,
                                                           "incidentRoadClosed": incidentRoadClosed,
                                                           "incidentStartTime": incidentStartTime,
                                                           "incidentEndTime": incidentEndTime,
                                                           "incidentEntryTime": incidentEntryTime,
                                                           "incidentCriticality": incidentCriticality,
                                                           "incidentComments": incidentComments,
                                                           "incidentLat_From": incidentLat_From,
                                                           "incidentLong_From": incidentLong_From,
                                                           "incidentLat_To": incidentLat_To,
                                                           "incidentLong_To": incidentLong_To,
                                                           "incidentRoadway_From": incidentRoadway_From,
                                                           "incidentRoadway_To": incidentRoadway_To})
                        except Exception as e:
                            logging.error(e)
                            print("Oops!  That was no valid traffic data.  Trying next one...")

                if len(incidentDicCSV) != 0:
                    try:
                        df_Traffic = pd.DataFrame(incidentDicCSV,
                                                  columns=("Timestamp", "incidentID", "incidentVerified",
                                                           "incidentType", "incidentRoadClosed", "incidentStartTime",
                                                           "incidentEndTime", "incidentEntryTime",
                                                           "incidentCriticality",
                                                           "incidentComments", "incidentLat_From", "incidentLong_From",
                                                           "incidentLat_To", "incidentLong_To", "incidentRoadway_From",
                                                           "incidentRoadway_To"))

                        timestr = datetime.utcnow().strftime("%Y%m%d")
                        if not os.path.isfile(dirName + fname.replace(".txt", "") + timestr + ".csv"):
                            HEADER_VAL = True
                            WRITE_MODE = "w+"
                        else:
                            HEADER_VAL = False
                            WRITE_MODE = "a"

                        df_Traffic.to_csv(dirName + fname.replace(".txt", "") + timestr + ".csv", sep=",", index=False,
                                          mode=WRITE_MODE, header=HEADER_VAL, encoding="utf-8")
                        logging.info("HERE_Incident: Converted csv file for " + str(dirName))
                    except Exception as x:
                        logging.error("Error creating the HERE_Incident csv file for " + str(dirName))
                        logging.error(x)


#   join CSV files and remove the individual ones
def join_csv_files(FOLDER, RemoveOriginal):
    for dirName, subdirList, fileList in os.walk(FOLDER):
        try:
            df_final = pd.DataFrame()
            # print('Found directory: %s' % dirName)
            for fname in fileList:
                if fname.find(".csv") != -1:  # checking .csv
                    df_final = df_final.append(pd.read_csv(dirName + fname, index_col=0))  # , sort=False)
                    if (RemoveOriginal == True):
                        os.remove(dirName + fname)
            df_final.to_csv(dirName + dirName.split("/")[1] + "_IncidentHERE.csv", sep=",", mode="a")
            logging.info("HERE_Incident: Joined csv file for " + str(dirName))
        except Exception as x:
            logging.error("Error joining the HERE_Incident csv files for " + str(dirName))
            logging.error(x)


#   remove all incident and traffic json files
def remove_txt_files(FOLDER):
    for dirName, subdirList, fileList in os.walk(FOLDER):
        # print('Found directory: %s' % dirName)
        for fname in fileList:
            if (fname.find(".txt") != -1):  # checking .txt
                os.remove(dirName + fname)


def main(city_list, time, logging_lvl):
    logging.basicConfig(filename='logfile.log', level=logging_lvl, format='%(asctime)s, %(levelname)s %(message)s',
                        datefmt='%Y-%m-%d,%H:%M:%S')

    for dir_name, subdir_list, file_list in os.walk(INPUT_DIR):
        # print('Found directory: %s' % dir_name)
        for subdir in subdir_list:
            if subdir in city_list:
                #   convert all incident json files into a filtered CSVs
                if os.path.isdir(INPUT_DIR + subdir + "/Traffic_HERE/"):
                    for dirs, subdirs, files in os.walk(INPUT_DIR + subdir + "/Traffic_HERE/"):
                        # print('Found subdirectory: %s' % dir_name)
                        #   convert all traffic json files in filtered CSVs
                        convert_traffic_to_csv(dirs)
                if os.path.isdir(INPUT_DIR + subdir + "/Incident_HERE/"):
                    #   convert all incident json files into a filtered CSVs
                    for dirs, subdirs, files in os.walk(INPUT_DIR + subdir + "/Incident_HERE/"):
                        # print('Found subdirectory: %s' % dir_name)

                        #   convert all incident json files in filtered CSVs
                        convert_incident_to_csv(dirs)

                        #   join CSV files and remove the individual ones
                        # joinCSVFiles(dir_name,True)

    #   remove all incident json files
    for dir_name, subdir_list, file_list in os.walk(INPUT_DIR):
        # print('Found directory: %s' % dir_name)
        for subdir in subdir_list:
            if subdir in city_list:
                for dirs, subdirs, files in os.walk(INPUT_DIR + subdir + "/Traffic_HERE/"):
                    remove_txt_files(dirs)
                    pass
                for dirs, subdirs, files in os.walk(INPUT_DIR + subdir + "/Incident_HERE/"):
                    remove_txt_files(dirs)
                    pass

    return True
