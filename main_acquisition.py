import data_acquisition.here_acquisition as here_acquire  # Data Acquisition: HERE
import data_acquisition.here_process as here_process  # Data Preprocessing: HERE
import data_acquisition.bing_acquisition as bing_acquire  # Data Acquisition : BING
import data_acquisition.bing_process as bing_process  # Data Preprocessing: BING
import data_acquisition.od as od  # Data Acquisition: Open Data
import data_acquisition.weather as weather  # Data Acquisition: Weather
import logging
import time
import configparser
import datetime

# Setup configuration file
configparser = configparser.RawConfigParser()
configFilePath = r'config.ini'
configparser.read(configFilePath)

# Load the acquisition interval and list of sources
time_val = int(configparser.get('main-config', 'time_interval'))
Sources = dict(configparser.items("Sources"))
Sources = {k: True if Sources[k] == 'true' else False for k in Sources}  # Convert to boolean

# Create a new logfile (ATTENTION: log file is recreated on each run of the script)
logging_lvl = logging.INFO
file = open("logfile.log", "w+")
file.close()

# Define all cities which should be covered by the data acquisition process
cities = ["bonn", "koeln", "hamburg", "berlin", "muenster", "moenchengladbach", "duesseldorf", "muenchen", "stuttgart",
          "dortmund", "bremen", "chemnitz"]

# Sets the starting date
startingDate = datetime.date.today()
acquired_today = False

while True:
    start_time = time.time()
    today = datetime.date.today()  # Gets the current date
    # HERE
    if Sources["traffic_here"]:
        here_acquire.main(cities, ["traffic"], time_val, logging_lvl)  # Collects HERE traffic data
    if Sources["incident_here"]:
        here_acquire.main(cities, ["incident"], time_val, logging_lvl)  # Collects HERE incident data
    if Sources["traffic_here"] or Sources["incident_here"]:
        here_process.main(cities, time_val, logging_lvl)  # Processes HERE data to csv format
    # BING
    if Sources["incident_bing"]:
        bing_acquire.main(cities, ["incident"], time_val, logging_lvl)  # Collects BING incident data
        bing_process.main(cities, time_val, logging_lvl)  # Converts BING data to csv
    # OpenData
    if Sources["traffic_od"]:
        od.main("bonn", "traffic", time_val, logging_lvl)  # Collects OD traffic data (Bonn)
        od.main("koeln", "traffic", time_val, logging_lvl)  # Collects OD traffic data (Cologne)
    if Sources["construction_od"]:
        od.main("bonn", "construction", time_val, logging_lvl)  # Collects OD construction data (Bonn)
        od.main("koeln", "construction", time_val, logging_lvl)  # Collects OD construction data (Cologne)
    # WEATHER
    if Sources["weather"]:
        if ((today - startingDate).days % 7 == 0) and not acquired_today:
            weather.main(cities, time_val, logging_lvl)
            acquired_today = True  # If the data has been acquired this flag is set to True
        elif (today - startingDate).days % 7 == 0:
            pass
        else:
            acquired_today = False  # On another day without data acquisition, the flag is set to false

    # Wait regarding the defined time interval until the next acquisition
    end_time = time.time()
    if (end_time - start_time) < time_val * 60:
        time.sleep(time_val * 60 - (end_time - start_time))
