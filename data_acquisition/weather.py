import bisect
import pandas as pd
import requests
import datetime as dt
import os
import json
import time
import logging


def process_html_to_csv(cityList, api_key):
    stationIDs = {
        "bonn": 10517,
        "koeln": 10513,
        "hamburg": 10147,
        "berlin": 10389,
        "muenster": 10315,
        "moenchengladbach": 10403,
        "duesseldorf": 10400,
        "muenchen": 10865,
        "stuttgart": 10739,
        "dortmund": 10416,
        "bremen": 10224,
        "chemnitz": 10577
    }

    latlong = {
        "bonn": [50.7, 7.15],
        "koeln": [50.8667, 7.1667],
        "hamburg": [53.6333, 10.0],
        "berlin": [52.5167, 13.4167],
        "muenster": [52.0087, 7.852],
        "moenchengladbach": [51.2333, 6.5],
        "duesseldorf": [51.3, 7667],
        "muenchen": [48.1333, 11.55],
        "stuttgart": [48.8333, 9.2],
        "dortmund": [51.5167, 7.6167],
        "bremen": [53.05, 8.8],
        "chemnitz": [50.8, 12.8667]
    }

    condition_arr = ["normal", "fog", "rain", "heavy_rain", "snowy", "rain", "snowy", "thunderstorm", "storm"]

    for city in cityList:  # iterating each city
        time.sleep(0.34)  # Wait 1/3 sec, because of the rate limit per second
        if not os.path.isdir("data_acquisition/data/" + city + "/Weather/"):
            os.makedirs("data_acquisition/data/" + city + "/Weather/")
        times = []
        precipitation = []
        snow = []
        latitude = []
        longitude = []
        temperature = []
        avg_windspeed = []
        peak_windspeed = []
        condition = []

        last_entry = False

        today = dt.date.today()
        id = stationIDs[city]
        start_date = (today - dt.timedelta(days=6)).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")  # Take current date as end and set start_date = today-7days
        headers = {"x-rapidapi-host": "meteostat.p.rapidapi.com",
                   "x-rapidapi-key": api_key}
        querystring = {"station": id, "start": start_date, "end": end_date, }  # The time is given in UTC format

        # try:
        response = requests.request("GET", "https://meteostat.p.rapidapi.com/stations/hourly", headers=headers,
                                    params=querystring, timeout=10)
        try:
            weather_data = json.loads(response.text)
        except:
            print("Error loading weather data (" + city + ")")
            logging.error("Error loading weather data (" + city + ")")
            continue

        # prev_date is used to distinct between the unique days and save the data for each day individually
        prev_date = dt.datetime.strptime(weather_data["data"][0]["time"], "%Y-%m-%d %H:%M:%S").date()
        for i, entry in enumerate(weather_data["data"]):
            if i == len(weather_data["data"]) - 1:
                # Case: Last entry to be processed
                last_entry = True
                times.append(entry["time"])
                temperature.append(entry["temp"])
                precipitation.append(entry["prcp"])
                snow.append(entry["snow"])
                avg_windspeed.append(entry["wspd"])
                peak_windspeed.append(entry["wpgt"])
                # latitude.append(latlong[city][0])
                # longitude.append(latlong[city][1])
                try:
                    raw_condition = bisect.bisect_left([4, 6, 8, 11, 16, 18, 22, 25], entry["coco"])
                except:
                    raw_condition = None
                condition.append(condition_arr[raw_condition])

            if dt.datetime.strptime(entry["time"], "%Y-%m-%d %H:%M:%S").date() != prev_date or last_entry:
                # Case: Processing a new date or reached the last value; Storing data in a dataframe
                df_weather = pd.concat([pd.Series(times, name='time'),
                                        # pd.Series(latitude, name='latitude'),
                                        # pd.Series(longitude, name='longitude'),
                                        pd.Series(temperature, name="temperature"),
                                        pd.Series(precipitation, name='precipitation_mm'),
                                        pd.Series(snow, name='snow_cm'),
                                        pd.Series(avg_windspeed, name="avg_windspeed"),
                                        pd.Series(peak_windspeed, name="peak_windspeed"),
                                        pd.Series(condition, name="weather_condition")], axis=1)

                df_weather.to_csv('data_acquisition/data/' + city + "/Weather/" + city + "_weather" + str(prev_date).replace("-", "") + ".csv",
                                  sep=',', mode="w+", header=True)  #
                prev_date = dt.datetime.strptime(entry["time"], "%Y-%m-%d %H:%M:%S").date()

                # Reset all lists when processing a new day
                times = []
                temperature = []
                precipitation = []
                snow = []
                avg_windspeed = []
                peak_windspeed = []
                condition = []
                # latitude = []
                # longitude = []

            times.append(dt.datetime.strptime(entry["time"], "%Y-%m-%d %H:%M:%S"))
            temperature.append(entry["temp"])
            precipitation.append(entry["prcp"])
            snow.append(entry["snow"])
            avg_windspeed.append(entry["wspd"])
            peak_windspeed.append(entry["wpgt"])
            try:
                raw_condition = bisect.bisect_left([4, 6, 8, 11, 16, 18, 22, 25], entry["coco"])
            except:
                raw_condition = None
            condition.append(condition_arr[raw_condition])

        print("Weather data acquired (" + city + ")")
        logging.info("Weather data acquired (" + city + ")")


def main(city_list, time, logging_lvl):
    keys = open("data_acquisition/api_keys.json")
    api_key_data = json.load(keys)
    api_key = api_key_data["rapidAPI_meteostat"]  # RapidAPI Key
    logging.basicConfig(filename='logfile.log', level=logging_lvl, format='%(asctime)s, %(levelname)s %(message)s',
                        datefmt='%Y-%m-%d,%H:%M:%S')

    process_html_to_csv(city_list, api_key)