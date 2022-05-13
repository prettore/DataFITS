# Import pandas package
import pandas as pd
import urllib.request
import json


#check manually the number of pages on https://envirocar.org/api/stable/sensors?page=NUMBEROFPAGES&limit=100
max_Page = 8 #6
page = 0

# list of cars and its features
car_list = []
vehicle_type = []
for page in range(page,max_Page + 1,1):

    object_Sensors = "https://envirocar.org/api/stable/sensors?page="+str(page)+"&limit=100"

    with urllib.request.urlopen(object_Sensors) as url:
        l = url.readlines()

        query_response_json = json.loads(l[0])

        #print(query_response_json)

        for sensors in query_response_json['sensors']:
            #if(sensors["type"] == "car"):
                #print(sensors["properties"])
            vehicle_type.append(sensors["type"])
            car_list.append(sensors["properties"])


df_Cars_temp = pd.DataFrame(car_list)
df_Cars = pd.concat([df_Cars_temp,pd.Series(vehicle_type, name='vehicle')], axis=1)
df_Cars.to_csv("Data/enviroCar_Cars.csv", sep=';')

