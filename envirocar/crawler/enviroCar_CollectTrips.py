# Import pandas package
import os
import pandas as pd
import json

# Execute the CollectCarAndTrip_ID before this step
df = pd.read_csv("Data/enviroCar_TimeTrip.csv", sep=',')

nRows = len(df.index)

for index, row in df.iterrows():
    # starting from the first observation (most recent) to the oldest one
    #if(index <= 1):

    # Read csv with semicolon as separator and one or more whitespaces after the semicolon
    df_Trip = pd.read_csv('https://envirocar.org/api/stable/tracks/' + row['trip_id'] + '.csv', sep=';\s+')

    # creating a car folders
    if(os.path.isdir("Data/Car-"+str(row['vehicle_id'])) == False):
        os.makedirs("Data/Car-"+str(row['vehicle_id']))

    #Convert dates to datetime
    df_Trip.time = pd.to_datetime(df_Trip.time, format='%Y-%m-%dT%H:%M:%SZ')
    # Set date as index
    df_Trip.set_index('time', inplace=True)
    # Set car id
    df_Trip['vehicle_id'] = pd.Series(str(row['vehicle_id']), index=df_Trip.index)

    # save csv in a folder car
    df_Trip.to_csv("Data/Car-"+str(row['vehicle_id'])+"/"+row['trip_id']+".csv", sep = ";")


    print("Track " + str(index) + " of "+ str(nRows) +" - ID: " + row['trip_id']+ " -> Finished.")

    print("Track " + str(index) +" -> Finished.")


