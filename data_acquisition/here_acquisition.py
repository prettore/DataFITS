import datetime
from datetime import datetime
from dateutil import tz
import os
import requests
import json
import configparser
import logging

keys = open("data_acquisition/api_keys.json")
api_key_data = json.load(keys)

# HERE MAPS
app_id_Here = api_key_data["app_id_Here"]
app_code_Here = api_key_data["app_code_Here"]

bound_boxes = []


# convert local datetime to utc date time
def get_UTCDate():
    # Auto-detect zones:
    to_zone = tz.tzutc()
    from_zone = tz.tzlocal()
    # utc = datetime.utcnow()
    start_date = datetime.now()
    # Tell the datetime object that it's in UTC time zone since
    # datetime objects are 'naive' by default
    utc = start_date.replace(tzinfo=from_zone)
    # Convert time zone
    start_date_UTC = utc.astimezone(to_zone)
    return start_date_UTC


# creating a station folders
def creatingFolders(dataFolder):
    if not os.path.isdir(dataFolder):
        os.makedirs(dataFolder)
    if not os.path.isdir(dataFolder + "/Traffic_HERE"):
        os.makedirs(dataFolder + "/Traffic_HERE")
    if not os.path.isdir(dataFolder + "/Incident_HERE"):
        os.makedirs(dataFolder + "/Incident_HERE")
    if not os.path.isdir(dataFolder + "/Incident_BING"):
        os.makedirs(dataFolder + "/Incident_BING")


# function to write a json file
def put(data, filename, date):
    try:
        fd = open(filename, 'a')
        fd.write(json.dumps(data) + "\n")
        fd.close()
    except:
        print('ERROR writing file -> ', filename, ' Date: ', str(date))


# collect traffic data from Here Maps
def crawler_Traffic():
    print("Crawler Traffic------" + str(get_UTCDate()))
    for city in cityFolders:
        city = city.lower()
        creatingFolders('data_acquisition/data/'+city)

        urlTraffic = "https://traffic.cit.api.here.com/traffic/6.1/flow.json?bbox=" + str(
            bound_boxes[city]) + "&app_id=" + app_id_Here + "&app_code=" + app_code_Here + "&responseattributes=sh,fc"
        print("HERE: " + str(urlTraffic))
        try:
            source_Traffic = requests.get(urlTraffic, timeout=5)
            put(json.loads(source_Traffic.text), 'data_acquisition/data/' + city + '/Traffic_HERE/' + city + '_trafficHERE.txt', get_UTCDate())
            logging.info("HERE traffic data acquired (" + city + ")")
            print(source_Traffic)
        except:
            print("ERROR: There is no response for HERE Traffic data in " + city)
            logging.error("There is no response for HERE Traffic data (" + city + ")")


# collect incidents data from Here Maps
def crawler_incident_here():
    print("Crawler Incident------" + str(get_UTCDate()))

    for city in cityFolders:
        city = city.lower()
        creatingFolders(city)

        urlIncident = "https://traffic.cit.api.here.com/traffic/6.0/incidents.json?bbox=" + \
                      str(bound_boxes[city]) + "&criticality=minor&app_id=" + app_id_Here + \
                      "&app_code=" + app_code_Here + "&responseattributes=sh,fc"
        print("HERE: " + str(urlIncident))
        try:
            source_Incident = requests.get(urlIncident, timeout=5)
            put(json.loads(source_Incident.text), 'data_acquisition/data/' + city + '/Incident_HERE/' + city + '_incidentHERE.txt', get_UTCDate())
            logging.info("HERE incident data acquired (" + city + ")")
        except:
            print("ERROR: There is no response for HERE Incident data in " + city)
            logging.error("There is no response for HERE Incident data (" + city + ")")


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

        if crawler == "traffic":
            crawler_Traffic()
        elif crawler == "incident":
            crawler_incident_here()

    return True
