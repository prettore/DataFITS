import json
import time
from networkx.readwrite.gml import read_gml
import pandas as pd
import requests
import os
import datetime
import logging
from datetime import timezone, tzinfo
import pytz
import networkx as nx

#Stuff necessary to convert to UTC time
local = pytz.timezone("Europe/Berlin")

def acquire_json(city, mode):
    '''
    Implement the acquisition of the json file from the OpenData website
    This could be done once a day e.g.; the data then could be saved to different daily csv files or appended to an existing one
    '''
    data = []

    if city == "bonn":
        if mode == "traffic":
            URL = "https://stadtplan.bonn.de/geojson?Thema=19584"
        elif mode == "construction":
            URL = "https://stadtplan.bonn.de/geojson?Thema=14403"
    elif city == "koeln":
        if mode == "traffic":
            URL="https://www.stadt-koeln.de/externe-dienste/open-data/traffic.php"
        elif mode == "construction":
            URL = "https://geoportal.stadt-koeln.de/arcgis/rest/services/verkehr/verkehrskalender/MapServer/0/query?where=objectid+is+not+null&text=&objectIds=&time=&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&distance=&units=esriSRUnit_Foot&relationParam=&outFields=*&returnGeometry=true&returnTrueCurves=false&maxAllowableOffset=&geometryPrecision=&outSR=4326&havingClause=&returnIdsOnly=false&returnCountOnly=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&returnZ=false&returnM=false&gdbVersion=&historicMoment=&returnDistinctValues=false&resultOffset=&resultRecordCount=&returnExtentOnly=false&datumTransformation=&parameterValues=&rangeValues=&quantizationParameters=&featureEncoding=esriDefault&f=pjson"
    elif city == "Hamburg":
        if mode == "traffic":
            #GML file; extension to xml
            URL="https://geodienste.hamburg.de/HH_WFS_Verkehrslage?SERVICE=WFS&VERSION=1.1.0&REQUEST=GetFeature&typename=de.hh.up:verkehrslage"

            #cords ar given in epsg (epsg: 25832) format and have to be converted into lat long (epsg: 4326)

    ###Trafic
    # https://opendata.bonn.de/dataset/stra%C3%9Fenverkehrslage-realtime (Real-time traffic URL)
    # https://stadtplan.bonn.de/geojson?Thema=19584 (link to json file)
    ### 

    if city == "hamburg":
        #G = read_gml(requests.get(URL, timeout=10).text)
        #return G
        pass
    elif city == "koeln" or city=="bonn":
        #This obtains data from the webpage. Dont request to often, because otherwise you will be temporarily blocked
        targetURL = URL
        try:
            data = json.loads(requests.get(targetURL, timeout= 10).text)
        except:
            logging.error("Error loading OD file for " + city +" -- " + mode)
        return data


def traffic_to_csv(data_name, WRITE_MODE, CITY_NAME):
    #threading.Timer((timeWaiting*60), traffic_to_csv, [data_name, "a", CITY_NAME]).start()
    data = acquire_json(CITY_NAME, data_name)
    
    timestr = datetime.datetime.utcnow().strftime("%Y%m%d")
    
    # Hamburg is not working with json data
    if CITY_NAME == "Hamburg":
        #print(list(data.nodes))
        pass

    try:
        if CITY_NAME == "koeln" and data_name == "construction":
            data = data["features"]   #Construction for koeln has some different structure
        else:
            data = data["features"]
    except:
        logging.error("Error fetching " + data_name + " Open Data for " + CITY_NAME)
        return 
    
    logging.info(data_name + " OpenData acquired (" + CITY_NAME+")")
    
    if CITY_NAME == "bonn":
        coordinates = []
        road_id = []
        times = []
        speed = []
        traffic_status = []

        if data_name == "traffic":
            '''
            Get all coordinates from one entry: traffic["features"][1]["geometry"]["coordinates"]
            Get all properties from one entry: traffic["features"][0]["properties"]
            '''
            for i in range (len(data)):
                coordinates.append(data[i]["geometry"]["coordinates"][0])
                road_id.append(data[i]["properties"]["strecke_id"])
                #Convert time to UTC
                time_obj = datetime.datetime.strptime(data[i]["properties"]["auswertezeit"], "%Y-%m-%dT%H:%M:%S")
                local_dt = local.localize(time_obj, is_dst=None)
                time_obj = local_dt.astimezone(pytz.utc)
                times.append(time_obj)
                speed.append(data[i]["properties"]["geschwindigkeit"])
                traffic_status.append(data[i]["properties"]["verkehrsstatus"])
            try:
                df = pd.DataFrame({'Cords':coordinates[:],'Road Id':road_id[:],'Time':times[:],'Speed':speed[:],'Traffic':traffic_status[:]})#.sort_values(by=['Time'])
                #print(df)

                if not os.path.isfile("./bonn/Traffic_OD/od_bonn_"+str(data_name)+timestr+".csv"):
                    HEADER_VAL = True
                    WRITE_MODE = "w+"
                else:
                    HEADER_VAL = False
                    WRITE_MODE = "a"

                df.to_csv("./bonn/Traffic_OD/od_bonn_"+str(data_name)+ timestr +".csv",index=False,encoding="utf-8", mode=WRITE_MODE, header=HEADER_VAL)
                #print("### Data aquired and saved ###")
            except Exception as x:
                logging.error("Error acquiring traffic open data for "+str(CITY_NAME))
                logging.error(x)

        elif data_name == "construction":

            coordinates = []
            baustelle_id = []
            bezeichnung = []
            times = []
            stadtbezirk = []
            stadtbezirk_bez = []
            adresse = []
            von = []
            bis = []
            traeger = []
            massnahme = []
            sperrung = []
            try:
                for i in range (len(data)):
                    coordinates.append(data[i]["geometry"]["coordinates"])
                    baustelle_id.append(data[i]["properties"]["baustelle_id"])
                    bezeichnung.append(data[i]["properties"]["bezeichnung"])
                    time_obj = datetime.datetime.utcnow()
                    times.append(time_obj)
                    stadtbezirk.append(data[i]["properties"]["stadtbezirk"])
                    stadtbezirk_bez.append(data[i]["properties"]["stadtbezirk_bez"])
                    adresse.append(data[i]["properties"]["adresse"])
                    von.append(data[i]["properties"]["von"])
                    bis.append(data[i]["properties"]["bis"])
                    traeger.append(data[i]["properties"]["traeger"])
                    massnahme.append(data[i]["properties"]["massnahme"])
                    sperrung.append(data[i]["properties"]["sperrung"])
            except:
                logging.error("Error creating datasets")
                return

            try:
                df = pd.DataFrame({'Cords':coordinates[:],'Construction Id':baustelle_id[:],'Desc':bezeichnung[:],'Time':times[:],'District':stadtbezirk[:],'District Id':stadtbezirk_bez[:],'Adress':adresse[:],'From':von[:],'To':bis[:],'Traeger':traeger[:],'Reason':massnahme[:],'Blockage':sperrung[:]})#.sort_values(by=['Time'])
                #print(df)

                if not os.path.isfile("./bonn/Construction_OD/od_bonn_"+str(data_name)+timestr+".csv"):
                    HEADER_VAL = True
                    WRITE_MODE = "w+"
                else:
                    HEADER_VAL = False
                    WRITE_MODE = "a"
                df.to_csv("./bonn/Construction_OD/od_bonn_"+str(data_name)+ timestr +".csv",index=False,encoding="utf-8", mode=WRITE_MODE, header=HEADER_VAL)
                #print("### Data aquired and saved ###")
            except Exception as x:
                logging.error("Error acquiring construction open data for "+str(CITY_NAME))
                logging.error(x)

    elif CITY_NAME == "koeln":

        coordinates = []
        identifier = []
        name = []
        traffic_status = []
        link = []
        times = []

        if data_name == "traffic":

            try:
                for i in range(len(data)):
                    coordinates.append(data[i]["geometry"]["paths"])
                    identifier.append(data[i]["attributes"]["identifier"])
                    name.append(data[i]["attributes"]["name"])
                    traffic_status.append(data[i]["attributes"]["auslastung"])
                    link.append(data[i]["attributes"]["link"])
                    time_obj = datetime.datetime.utcnow()
                    times.append(time_obj)
            except:
                    logging.error("Error creating datasets")
                    return
            try:
                df = pd.DataFrame({'Cords':coordinates[:], 'ID':identifier[:], 'Time':times[:], 'Name':name[:], 'Traffic':traffic_status[:], 'Link':link[:]})
                #print(df)

                if not os.path.isfile("./koeln/Traffic_OD/od_koeln_"+str(data_name)+timestr+".csv"):
                    HEADER_VAL = True
                    WRITE_MODE = "w+"
                else:
                    HEADER_VAL = False
                    WRITE_MODE = "a"
                df.to_csv("./koeln/Traffic_OD/od_koeln_"+str(data_name)+ timestr +".csv",index=False,encoding="utf-8", mode=WRITE_MODE, header=HEADER_VAL)
            except Exception as x:
                    logging.error("Error acquiring traffic open data for "+str(CITY_NAME))
                    logging.error(x)

        elif data_name == "construction":
            typ_dict={
                1 : "Warning",
                2 : "Road Blockage",    #Baustelle, keine einfahrt
                3 : "Construction",
                4 : "Kids on street",
                5 : "Congestion",
                6 : "Slippery road",
                7 : "Flood"
            }

            coordinates = []
            object_id = []
            times = []
            adresse = []
            von = []
            bis = []
            typ = []
            desc = []
            try:
                for i in range (len(data)):
                    coordinates.append([data[i]["geometry"]["x"],data[i]["geometry"]["y"]])
                    object_id.append(data[i]["attributes"]["objectid"])
                    time_obj = datetime.datetime.utcnow()
                    times.append(time_obj)
                    adresse.append(data[i]["attributes"]["name"])
                    von.append(data[i]["attributes"]["datum_von"])
                    bis.append(data[i]["attributes"]["datum_bis"])
                    typ.append(typ_dict.get(data[i]["attributes"]["typ"], "Event"))
                    desc.append(data[i]["attributes"]["beschreibung"])
            except:
                logging.error("Error creating datasets")
                return

            try:
                df = pd.DataFrame({'Cords':coordinates[:],'Construction Id':object_id[:],'Time':times[:],'Adress':adresse[:],'From':von[:],'To':bis[:],'Typ':typ[:]})#.sort_values(by=['Time'])
                #print(df)

                if not os.path.isfile("./koeln/Construction_OD/od_koeln_"+str(data_name)+timestr+".csv"):
                    HEADER_VAL = True
                    WRITE_MODE = "w+"
                else:
                    HEADER_VAL = False
                    WRITE_MODE = "a"
                df.to_csv("./koeln/Construction_OD/od_koeln_"+str(data_name)+ timestr +".csv",index=False,encoding="utf-8", mode=WRITE_MODE, header=HEADER_VAL)
                #print("### Data aquired and saved ###")
            except Exception as x:
                logging.error("Error acquiring construction open data for "+str(CITY_NAME))
                logging.error(x)

#f = open("../FrameworkPlanning/Data/e_loading_stations.json","r")
#e_loading_stations = json.load(f)

# f = open("../FrameworkPlanning/Data/parking_stations.json","r")
# parking_stations = json.load(f)

timeWaiting = 0 #min


def main(searchCity, mode, time, logging_lvl):
    global timeWaiting
    timeWaiting = time
    cities = ["bonn","koeln"]

    logging.basicConfig(filename='logfile.log', level=logging_lvl, format='%(asctime)s, %(levelname)s %(message)s',datefmt='%Y-%m-%d,%H:%M:%S')

    for city in cities:
        if (os.path.isdir('./'+city+'/') == False):
            os.makedirs('./'+city+'/')    #Creates the od folders to save the data
        if (os.path.isdir('./'+city+'/Construction_OD/') == False):
            os.makedirs('./'+city+'/Construction_OD')
        if (os.path.isdir('./'+city+'/Traffic_OD/') == False):
            os.makedirs('./'+city+'/Traffic_OD')
    
    traffic_to_csv(mode, WRITE_MODE = "a", CITY_NAME = searchCity)

    return True
    #print(json.dumps(traffic,indent=2, ensure_ascii=False))

if __name__=="__main__":
    main(searchCity = "bonn", mode="traffic", time=10)
    '''
    - Choose city between "bonn" and "koeln"
    - Choose mode between "traffic" and "construction"
    '''