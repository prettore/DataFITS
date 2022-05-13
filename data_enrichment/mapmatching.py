from fmm import UBODTGenAlgorithm,Network,NetworkGraph,FastMapMatch,FastMapMatchConfig,GPSConfig,ResultConfig,UBODT,STMATCH,STMATCHConfig
import pandas as pd
import configparser
from os.path import exists
#network = Network("../data/edges.shp")

'''
SET THE CITY in the network and ubodt generation manually
'''


def fmm(SOURCE,createUBODT,mode):
    global CITY
    network = Network(CITY+"/edges.shp", "fid", "u", "v") #Read the network from shape file
    graph = NetworkGraph(network)
    print (graph.get_num_vertices())

    #wkt = "LINESTRING(0.200812146892656 2.14088983050848,1.44262005649717 2.14879943502825,3.06408898305084 2.16066384180791,3.06408898305084 2.7103813559322,3.70872175141242 2.97930790960452,4.11606638418078 2.62337570621469)"

    if createUBODT:
        #if os.path.exists(CITY+"/ubodt.txt"):
            #os.remove(CITY+"/ubodt.txt")
        ubodt_gen = UBODTGenAlgorithm(network,graph) #generate ubodt
        status = ubodt_gen.generate_ubodt(CITY+"/ubodt.txt", 0.1, binary=False, use_omp=True)
        print (status)
    #ubodt = UBODT.read_ubodt_csv("./bonn/ubodt.txt") #read ubotd from file
    if mode == "fmm":
        model = ST(network,graph,ubodt)
    elif mode == "stmatch":
        model = STMATCH(network, graph)

    k = 8
    radius = 0.4
    gps_error = 0.2
    #vmax = 30
    #factor = 1.5
    if mode == "fmm":
        fmm_config = FastMapMatchConfig(k,radius,gps_error)
    elif mode == "stmatch":
        stmatch_config = STMATCHConfig(k, radius, gps_error) 

    input_config = GPSConfig()
    input_config.file = "fmm_input/trips_"+SOURCE+".csv" #Contains the linestrings which should be matched to the network
    input_config.id = "id"
    print (input_config.to_string())
    result_config = ResultConfig()
    result_config.file = "fmm_output/output_"+SOURCE+".csv"
    result_config.output_config.write_opath = True
    print (result_config.to_string())
    if mode == "fmm":
        status = model.match_gps_file(input_config, result_config, fmm_config)
    elif mode == "stmatch":
        status = model.match_gps_file(input_config, result_config, stmatch_config)

    print(status)


#!!! Configparser not really working because of python2!!!
#Setup config file
configparser = configparser.RawConfigParser()
configFilePath = r'../config.ini'
configparser.read(configFilePath)

Sources = configparser.options("Sources")

CITY = str(configparser.get("main-config","city").lower())

# UBODT file is created if it not exists
if (exists("./"+CITY+"/ubodt.txt")):
    # Manually set to true if the SHP was changed, 
    # It's necessary to reconstruct ubodt on any change to the SHP
    createUBODT = False
else:
    createUBODT = True

for source in Sources:
    SOURCE =  str(source).upper()
    print("Processing %s ..." % SOURCE)
    if (SOURCE == "ADAC" or SOURCE == "WEATHER"):
        print(SOURCE + " is not implemented yet")
        continue
    fmm(SOURCE, createUBODT, mode="stmatch")
    #We only need to create the ubodt file once
    createUBODT = False
