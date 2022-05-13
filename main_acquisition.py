import data_acquisition.od_acquisition as od                            #Gets Traffic and Construction data from OpenData
import traffic.crawler.Traffic_Crawler as Main_Crawler                  #Gets the data from HERE, BING and MAPQUEST
import traffic.crawler.ConvertHERE_Traffic_Incident_ToCSV as HERE_CSV   #Converts the HERE data to csv files
import traffic.crawler.ConvertBING_Incident_ToCSV as BING_CSV           #Converts the BING data to csv files
import data_acquisition.adac_crawler as adac                            #Acquires Data from ADAC
import weather.crawler.Weather_Crawler as Weather_Crawler              #Acquires Weather Data (1 time a week; hourly data)
import logging
import time
import configparser
import datetime


configparser = configparser.RawConfigParser()
configFilePath = r'config.ini'
configparser.read(configFilePath)

time_val = int(configparser.get('main-config','time_interval')) #default: 10 minutes
Sources = configparser.options("Sources")

#Create a new logfile (ATTENTION: The old log file will be deleted when you run this script)
file = open("logfile.log","w+")
file.close()
'''
Logging is done in each module itself
'''
logging_lvl = logging.INFO

'''Here you can define all the cities for the data acquisition'''
cities = ["bonn","koeln","hamburg","berlin","muenster","moenchengladbach","duesseldorf","muenchen","stuttgart","dortmund","bremen","chemnitz"]

#Sets the starting date
startingDate = datetime.date.today()
acquired_today = False
while True:
    start_time = time.time()
    today = datetime.date.today()    #Gets the current date
    if "traffic_here" in Sources:
        Main_Crawler.main(cities,["traffic"],time_val,logging_lvl) #Collects traffic data from HERE
    if "incident_here" in Sources:
        Main_Crawler.main(cities,["incident_here"],time_val,logging_lvl) #Collects incident data from HERE
    if "traffic_here" or "incident_here" in Sources:
        HERE_CSV.main(cities,time_val, logging_lvl) #Convert HERE traffic to csv
    if "incident_bing" in Sources:
        Main_Crawler.main(cities, ["incident_bing"],time_val,logging_lvl)
        BING_CSV.main(cities, time_val, logging_lvl) #Convert BING incident to csv

    if "traffic_od" in Sources:
        od.main("bonn", "traffic", time_val, logging_lvl)  # Acquires traffic data for bonn every 10 mins
        od.main("koeln", "traffic", time_val, logging_lvl) # Acquires traffic data for cologne every 10 mins
        #od.main("Hamburg", "traffic", time_val, logging_lvl) #Implement OD for Hamburg
    if "construction_od" in Sources:
        od.main("bonn","construction", time_val, logging_lvl) # Acquires construction data for bonn every 10 mins
        od.main("koeln", "construction", time_val, logging_lvl)

    if "adac" in Sources:
        adac.main(cities, time_val, logging_lvl) #Acquires traffic and construction data for Bonn (and 25km around) from ADAC every 10 mins
    
    if "weather" in Sources:
        if ((today-startingDate).days % 7 == 0) and not acquired_today:
            Weather_Crawler.main(cities,time_val,logging_lvl)
            acquired_today = True #If the data has been acquired this flag is set to True
        elif ((today-startingDate).days % 7 == 0):
            pass
        else:
            acquired_today = False #On another day without data acquisition, the flag is set to false
    end_time = time.time()
    time.sleep(time_val*60-(end_time-start_time))
