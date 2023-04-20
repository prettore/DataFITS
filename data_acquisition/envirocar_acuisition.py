import pandas as pd
import urllib.request
import json
import os


def collect_cars_trips_id(max_page):
    page = 0
    # list of tracks(trips) and its length
    vehicle_type = []
    car_list = []
    trip_list = []
    trip_Distance_km_list = []
    df_TimeTrip = pd.DataFrame()

    print('Checking for Envirocar Data...\n')

    # creating envirocar folder
    if not os.path.isdir("data_acquisition/envirocar_data/total"):
        os.makedirs("data_acquisition/envirocar_data/total")

    for page in range(page, max_page + 1, 1):

        object_Sensors = "https://envirocar.org/api/stable/tracks?page=" + str(page) + "&limit=100"
        # query_sensors = urllib.urlopen(object_Sensors)

        with urllib.request.urlopen(object_Sensors) as url:
            l = url.readlines()
            # l = query_sensors.readlines()
            query_response_json = json.loads(l[0])

            # print(query_response_json)
            for track in query_response_json['tracks']:

                trip_list.append({"trip_id": track["id"],
                                  "trip_begin": pd.to_datetime(track["begin"], format='%Y-%m-%dT%H:%M:%SZ'),
                                  "trip_end": pd.to_datetime(track["end"], format='%Y-%m-%dT%H:%M:%SZ')})

                # trip_Id_list.append(track["id"])
                # trip_Id_list.append(track["begin"])
                # trip_Id_list.append(track["end"])
                if 'length' in track:
                    trip_Distance_km_list.append(track["length"])
                else:
                    trip_Distance_km_list.append(0)

                # car_list.append(track["sensor"]["properties"]["id"])
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

            print(f"\rCollecting Data: {page / max_page * 100:.2f} %", end="")

    df_Trip = pd.DataFrame(trip_list)
    df_Cars = pd.DataFrame(car_list)

    df_TimeTrip = pd.concat([df_Trip, pd.Series(trip_Distance_km_list, name='trip_Distance_km'),
                             df_Cars, pd.Series(vehicle_type, name='vehicle')], axis=1)

    df_TimeTrip.to_csv("data_acquisition/envirocar_data/total/enviroCar_TimeTrip.csv", index=False, sep=',')


def collect_cars_features(max_page):
    page = 0
    # list of cars and its features
    car_list = []
    vehicle_type = []
    for page in range(page, max_page + 1, 1):

        object_Sensors = "https://envirocar.org/api/stable/sensors?page=" + str(page) + "&limit=100"

        with urllib.request.urlopen(object_Sensors) as url:
            l = url.readlines()

            query_response_json = json.loads(l[0])

            for sensors in query_response_json['sensors']:
                # if(sensors["type"] == "car"):
                # print(sensors["properties"])
                vehicle_type.append(sensors["type"])
                car_list.append(sensors["properties"])

    df_Cars_temp = pd.DataFrame(car_list)
    df_Cars = pd.concat([df_Cars_temp, pd.Series(vehicle_type, name='vehicle')], axis=1)
    df_Cars.to_csv("data_acquisition/envirocar_data/total/enviroCar_Cars.csv", sep=';')


def collect_trips():
    df = pd.read_csv("data_acquisition/envirocar_data/total/enviroCar_TimeTrip.csv", sep=',')

    nRows = len(df.index)

    for index, row in df.iterrows():
        # starting from the first observation (most recent) to the oldest one
        # if(index <= 1):

        # Read csv with semicolon as separator and one or more whitespaces after the semicolon
        df_Trip = pd.read_csv('https://envirocar.org/api/stable/tracks/' + row['trip_id'] + '.csv', sep=';\s+', engine='python')

        # creating a car folders
        if not os.path.isdir("data_acquisition/envirocar_data/total/Car-" + str(row['vehicle_id'])):
            os.makedirs("data_acquisition/envirocar_data/total/Car-" + str(row['vehicle_id']))

        # Convert dates to datetime
        df_Trip.time = pd.to_datetime(df_Trip.time, format='%Y-%m-%dT%H:%M:%SZ')
        # Set date as index
        df_Trip.set_index('time', inplace=True)
        # Set car id
        df_Trip['vehicle_id'] = pd.Series(str(row['vehicle_id']), index=df_Trip.index)

        # save csv in a folder car
        df_Trip.to_csv("data_acquisition/envirocar_data/total/Car-" + str(row['vehicle_id']) + "/" + row['trip_id'] + ".csv", sep=";")

        print(f"\rProcessing Data: {index / nRows * 100:.2f} %", end="")


def main():
    # check manually the number of pages on https://envirocar.org/api/stable/tracks?page=NUMBEROFPAGES&limit=100
    max_tracks = 240
    collect_cars_trips_id(max_tracks)

    # check manually the number of pages on https://envirocar.org/api/stable/sensors?page=NUMBEROFPAGES&limit=100
    max_sensors = 9
    collect_cars_features(max_sensors)

    collect_trips()

    print('--> Finished collecting and processing Envirocar data')


if __name__ == '__main__':
    main()
