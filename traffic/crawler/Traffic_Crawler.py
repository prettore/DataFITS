import datetime
from datetime import datetime
from dateutil import tz
import os
import requests
import json
import configparser
import logging

keys = open("api_keys.json")
api_key_data = json.load(keys)
api_key = api_key_data["rapidAPI_meteostat"] #RapidAPI Key

##HERE MAPS
#Here Maps user id
app_id_Here = api_key_data["app_id_Here"] 
app_code_Here =api_key_data["app_code_Here"] 


##BING MAPS
#https://msdn.microsoft.com/en-us/library/hh441726.aspx
#https://www.bingmapsportal.com/?lc=1033
app_key_Bing = api_key_data["app_key_Bing"]
#"AtlvD9CKbWQUtUQC-qmKEKek6OT__cRxwuK78WdX9rwqKAiDfSvPEQv8OhpbDu55"

bound_boxes = []

# conver local datetime to utc date time
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
    if (os.path.isdir(dataFolder) == False):
        os.makedirs(dataFolder)
    if (os.path.isdir(dataFolder + "/TrafficHERE") == False):
        os.makedirs(dataFolder + "/TrafficHERE")
    if (os.path.isdir(dataFolder + "/IncidentHERE") == False):
        os.makedirs(dataFolder + "/IncidentHERE")
    if (os.path.isdir(dataFolder + "/IncidentBING") == False):
        os.makedirs(dataFolder + "/IncidentBING")
    #if (os.path.isdir(dataFolder + "/IncidentMAPQUEST") == False):
    #    os.makedirs(dataFolder + "/IncidentMAPQUEST")
    #if (os.path.isdir(dataFolder + "/WeatherHERE") == False):
    #    os.makedirs(dataFolder + "/WeatherHERE")


# function to write a json file
def put(data, filename, date):
	try:
		fd = open(filename, 'a')
		fd.write(json.dumps(data)+"\n")
		fd.close()
	except:
		print('ERROR writing file -> ', filename, ' Date: ', str(date))

# collect traffic data from Here Maps
def crawler_Traffic():
    print("Crawler Traffic------" + str(get_UTCDate()))
    for city in cityFolders:
        city = city.lower()
        creatingFolders(city)

        urlTraffic = "https://traffic.cit.api.here.com/traffic/6.1/flow.json?bbox="+str(bound_boxes[city])+"&app_id="+app_id_Here+"&app_code="+app_code_Here+"&responseattributes=sh,fc"
        print("HERE: " + str(urlTraffic))
        try:
            source_Traffic = requests.get(urlTraffic, timeout= 10)
            put(json.loads(source_Traffic.text), city+'/TrafficHERE/'+ city+ '_trafficHERE.txt', get_UTCDate())
            logging.info("HERE traffic data acquired ("+city+")")
            print(source_Traffic)
        except:
            print("ERROR: There is no response for Incident data in "+city)
            logging.error("There is no response for Incident data ("+city+")")


# collect incidents data from Here Maps
def crawler_incident_here():
    print("Crawler Incident------" + str(get_UTCDate()))
    
    for city in cityFolders:
      city = city.lower()
      creatingFolders(city)


      urlIncident = "https://traffic.cit.api.here.com/traffic/6.0/incidents.json?bbox=" + str(bound_boxes[city]) + "&criticality=minor&app_id=" + app_id_Here + "&app_code=" + app_code_Here + "&responseattributes=sh,fc"
      print("HERE: " + str(urlIncident))
      try:
        source_Incident = requests.get(urlIncident, timeout= 10)
        put(json.loads(source_Incident.text), city + '/IncidentHERE/' +  city+ '_incidentHERE.txt', get_UTCDate())
        logging.info("HERE incident data acquired ("+city+")")
      except:
        print("ERROR: There is no response for Incident data in "+city)
        logging.error("There is no response for Incident data ("+city+")")

def crawler_incident_bing():
    for city in cityFolders:
      city = city.lower()
      urlIncident = "http://dev.virtualearth.net/REST/v1/Traffic/Incidents/" + str(bound_boxes[city]).replace(";", ",") + "?key="+app_key_Bing
      print("BING: " + str(urlIncident))
      try:
        source_Incident = requests.get(urlIncident, timeout= 10)
        put(json.loads(source_Incident.text), city + '/IncidentBING/' + city+ '_incidentBING.txt',
              get_UTCDate())
        logging.info("BING incident data acquired ("+city+")")
      except:
        print("ERROR: There is no response for Incident data in "+city)
        logging.error("There is no response for Incident data ("+city+")")

#def crawler_incident_mapquest():
#    for city in cityFolders:
#       city = city.lower()
    #   urlIncident = "http://www.mapquestapi.com/traffic/v2/incidents?key=" + app_consumer_key_Mapquest + "&boundingBox=" + str(bound_boxes[i][0]).replace(";", ",") + "&filters=incidents,congestion,event,construction"
    #   print("MAPQUEST: " + str(urlIncident))
    #   try:
    #     source_Incident = requests.get(urlIncident, timeout= 10)
    #     put(json.loads(source_Incident.text), cityFolders[i] + '/IncidentMAPQUEST/' +  cityFolders[i]+ '_incidentMAPQUEST.txt',
    #           get_UTCDate())
    #     logging.info("MAPQUEST incident data acquired ("+cityFolders[i]+")")
    #   except:
    #         logging.error("Connection problem with MAPQUEST")
    #         print("ERROR: There is no response for Incident data in "+cityFolders[i])
    #         logging.error("There is no response for Incident data ("+cityFolders[i]+")")


# collect weather data from Here Maps ***Limited access for the trial account
def crawler_Weather():
  print("Crawler Weather------" + str(get_UTCDate()))
  for city in cityFolders:
      city = city.lower()
      creatingFolders(city)
      
      urlWeather = "https://weather.cit.api.here.com/weather/1.0/report.json?product=observation&name=" + str(
          city) + "&app_id=" + app_id_Here + "&app_code=" + app_code_Here

      print(str(urlWeather))
      try:
        source_Weather = requests.get(urlWeather, timeout= 10)
        put(json.loads(source_Weather.text),
              city + '/Weather/' + str(get_UTCDate().date()) + '.txt', get_UTCDate())
        logging.info("Weather data acquired ("+city+")")
      except:
            logging.error("Connection problem with WEATHER")
            print("ERROR: There is no response for Weather data in "+city+ "on" + str(get_UTCDate()))
            logging.error("There is no response for Weather data ("+city+"on "+str(get_UTCDate())+")")


def main(city_list, mode_list, time, logging_lvl):
    import configparser
    logging.basicConfig(filename='logfile.log', level=logging_lvl, format='%(asctime)s, %(levelname)s %(message)s',datefmt='%Y-%m-%d,%H:%M:%S')
    #threading.Timer((time*60), main, [city_list, mode_list, time, logging_lvl]).start()
    global bound_boxes, cityFolders
    cityFolders = city_list

    configparser = configparser.RawConfigParser()
    configFilePath = r'./config.ini'
    configparser.read(configFilePath)

    bound_boxes = configparser._sections["BB-Config"]

    for crawler in mode_list:

        if crawler == "traffic":
            crawler_Traffic()
        elif crawler == "incident_here":
            crawler_incident_here()
        elif crawler == "incident_bing":
            crawler_incident_bing()
        elif crawler == "weather":
            crawler_Weather()


    return True
