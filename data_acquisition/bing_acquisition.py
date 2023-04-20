import datetime
from datetime import datetime
from dateutil import tz
import os
import requests
import json
import configparser
import logging
from data_acquisition.here_acquisition import put
from data_acquisition.here_acquisition import get_UTCDate


keys = open("data_acquisition/api_keys.json")
api_key_data = json.load(keys)

# BING MAPS
app_key_Bing = api_key_data["app_key_Bing"]

# creating a station folders
def creatingFolders(dataFolder):
    if not os.path.isdir(dataFolder):
        os.makedirs(dataFolder)
    if not os.path.isdir(dataFolder + "/Incident_BING"):
        os.makedirs(dataFolder + "/Incident_BING")

def crawler_incident_bing():
    for city in cityFolders:
        city = city.lower()
        creatingFolders('data_acquisition/data/'+city)
        url_incident = "http://dev.virtualearth.net/REST/v1/Traffic/Incidents/" + str(bound_boxes[city]).replace \
            (";", ",") + "?key=" + app_key_Bing
        print("BING: " + str(url_incident))
        try:
            source_incident = requests.get(url_incident, timeout=5)
            put(json.loads(source_incident.text), 'data_acquisition/data/' + city + '/Incident_BING/' + city + '_incidentBING.txt',
                get_UTCDate())
            logging.info("BING incident data acquired (" + city + ")")
        except:
            print("ERROR: There is no response for BING Incident data in " + city)
            logging.error("There is no response for BING Incident data (" + city + ")")


def main(city_list, mode_list, time, logging_lvl):
    import configparser
    logging.basicConfig(filename='logfile.log', level=logging_lvl, format='%(asctime)s, %(levelname)s %(message)s',
                        datefmt='%Y-%m-%d,%H:%M:%S')
    # threading.Timer((time*60), main, [city_list, mode_list, time, logging_lvl]).start()
    global bound_boxes, cityFolders
    cityFolders = city_list

    configparser = configparser.RawConfigParser()
    config_filepath = r'./config.ini'
    configparser.read(config_filepath)

    bound_boxes = configparser._sections["BB-Config"]

    for crawler in mode_list:

        if crawler == "incident":
            crawler_incident_bing()

    return True
