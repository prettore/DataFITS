# Import pandas package
import pandas as pd
import urllib.request
import json

#check manually the number of pages on https://envirocar.org/api/stable/tracks?page=NUMBEROFPAGES&limit=100
max_Page = 235 #185
page = 0
# list of traks(trips) and its length
vehicle_type = []
car_list = []
trip_list = []
trip_Distance_km_list = []
df_TimeTrip = pd.DataFrame()
for page in range(page,max_Page + 1,1):

    object_Sensors = "https://envirocar.org/api/stable/tracks?page=" + str(page) + "&limit=100"
    #query_sensors = urllib.urlopen(object_Sensors)



    with urllib.request.urlopen(object_Sensors) as url:
        l = url.readlines()
        #l = query_sensors.readlines()
        query_response_json = json.loads(l[0])

        #print(query_response_json)
        for track in query_response_json['tracks']:

            trip_list.append({"trip_id": track["id"],
                              "trip_begin": pd.to_datetime(track["begin"], format='%Y-%m-%dT%H:%M:%SZ'),
                              "trip_end": pd.to_datetime(track["end"], format='%Y-%m-%dT%H:%M:%SZ')})

            #trip_Id_list.append(track["id"])
            #trip_Id_list.append(track["begin"])
            #trip_Id_list.append(track["end"])
            if 'length' in track:
                trip_Distance_km_list.append(track["length"])
            else:
                trip_Distance_km_list.append(0)

            #car_list.append(track["sensor"]["properties"]["id"])
            vehicle_type.append(track["sensor"]["type"])

            engineDisplacement = 0
            model = 0
            fuelType = 0
            constructionYear = 0
            manufacturer = 0
            if 'engineDisplacement' in track["sensor"]["properties"]:
                engineDisplacement = track["sensor"]["properties"]["engineDisplacement"]
            if 'model' in track["sensor"]["properties"]:
                model = track["sensor"]["properties"]["model"]
            if 'fuelType' in track["sensor"]["properties"]:
                fuelType = track["sensor"]["properties"]["fuelType"]
            if 'constructionYear' in track["sensor"]["properties"]:
                constructionYear = track["sensor"]["properties"]["constructionYear"]
            if 'manufacturer' in track["sensor"]["properties"]:
                manufacturer = track["sensor"]["properties"]["manufacturer"]

            car_list.append({"vehicle_id": track["sensor"]["properties"]["id"],
                             "vehicle_engineDisplacement": engineDisplacement,
                             "vehicle_model": model,
                             "vehicle_fuelType": fuelType,
                             "vehicle_year": constructionYear,
                             "vehicle_manufacturer": manufacturer})

        print("Page:" + str(page) + " -> Finished.")

df_Trip = pd.DataFrame(trip_list)
df_Cars = pd.DataFrame(car_list)

df_TimeTrip = pd.concat([df_Trip, pd.Series(trip_Distance_km_list, name='trip_Distance_km'),
                         df_Cars,pd.Series(vehicle_type, name='vehicle')], axis=1)

#df_TimeTrip = pd.concat([df_TimeTrip,pd.Series(car_list, name='car_Id'),pd.Series(trip_list, name='trip_Id')
#                            ,pd.Series(trip_Distance_km_list, name='trip_Distance_km')], axis=1)


df_TimeTrip.to_csv("Data/enviroCar_TimeTrip.csv",index=False, sep=',')

