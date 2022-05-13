import pandas as pd
import requests
from datetime import timedelta, date
import os
import json
import time
import logging

def processHTMLtoCSV(cityList,api_key):

    stationIDs = {
        "bonn": 10517,
        "koeln":10513,
        "hamburg":10147,
        "berlin":10389,
        "muenster":"D3669",
        "moenchengladbach":10403,
        "duesseldorf":10400,
        "muenchen":10865,
        "stuttgart":10739,
        "dortmund":10416,
        "bremen":10224,
        "chemnitz":10577
    }

    latlong = {
        "bonn":[50.7,7.15],
        "koeln":[50.8667, 7.1667],
        "hamburg":[53.6333,10.0],
        "berlin":[52.5167,13.4167],
        "muenster":[52.0087,7.852],
        "moenchengladbach":[51.2333, 6.5],
        "duesseldorf":[51.3,7667],
        "muenchen":[48.1333,11.55],
        "stuttgart":[48.8333,9.2],
        "dortmund":[51.5167,7.6167],
        "bremen":[53.05,8.8],
        "chemnitz":[50.8,12.8667]
    }

    for city in cityList:    #   iterating each city
        time.sleep(0.34)   #Wait 1/3 sec, because of the rate limit per second
        if (os.path.isdir(city+"/Weather/") == False):
            os.makedirs(city+"/Weather/")
        weatherDate = []
        precipitation = []
        snow = []
        latitude = []
        longitude = []
        temperature = []

        today = date.today()
        id = stationIDs[city]
        startDate = (today - timedelta(days=6)).strftime("%Y-%m-%d")   
        endDate = today.strftime("%Y-%m-%d")      #Take current date as end and set startDate = today-7days
        headers = {"x-rapidapi-host":"meteostat.p.rapidapi.com",
	                "x-rapidapi-key": api_key}
        querystring = {"station":id,"start":startDate,"end":endDate,}   #The time is given in UTC format
        
        #try:
        response = requests.request("GET", "https://meteostat.p.rapidapi.com/stations/hourly", headers=headers, params=querystring, timeout=10)
        weatherData = json.loads(response.text)
        for entry in weatherData["data"]:
            weatherDate.append(entry["time"])
            temperature.append(entry["temp"])
            precipitation.append(entry["prcp"])
            snow.append(entry["snow"])
            latitude.append(latlong[city][0])
            longitude.append(latlong[city][1])

        df_weather = pd.concat([pd.Series(weatherDate, name='date'),
                                pd.Series(latitude, name='latitude'),
                                pd.Series(longitude, name='longitude'),
                                pd.Series(temperature, name="temperature"),
                                pd.Series(precipitation, name='precipitation_mm'),
                                pd.Series(snow, name='snow_cm')], axis=1)


        if not os.path.isfile(city+"/Weather/" +"WeatherData_"+city+".csv"):
            HEADER_VAL = True
            WRITE_MODE = "w+"
        else:
            HEADER_VAL = False
            WRITE_MODE = "a"

        df_weather.to_csv(city+"/Weather/" +"WeatherData_"+city+".csv", sep=',', mode=WRITE_MODE, header=HEADER_VAL)#

        print("Weather data acquired ("+city+")")
        logging.info("Weather data acquired ("+city+")")
        #except:
            # print("ERROR: There is no response for weather data in " + city)
            # print(response.status_code)
            # logging.error("There is no response for weather data ("+city+")")

def main(city_list, time, logging_lvl):

    keys = open("api_keys.json")
    api_key_data = json.load(keys)
    api_key = api_key_data["rapidAPI_meteostat"] #RapidAPI Key
    logging.basicConfig(filename='logfile.log', level=logging_lvl, format='%(asctime)s, %(levelname)s %(message)s',datefmt='%Y-%m-%d,%H:%M:%S')
    
    processHTMLtoCSV(city_list,api_key)


if __name__ == "__main__":
    main(["bonn","koeln","hamburg","berlin","muenster","moenchengladbach","duesseldorf"],time=10,logging_lvl=logging.INFO)
