# DataFITS - Data Fusion Framework for ITS

This project is a framework, capable of collecting heterogeneous data from different sources which can be used to develop new applications in the context of Intelligent Transportation Systems. DataFITS collects data and processes it through the use of mapmatching, fusing it regarding spatiotemporal aspects resulting in an enrichment of the acquired information. The framework is developed in Python3 but the mapmatching algorithm uses Python2.7.

![Alt text](img/DataFITS_overview.png?raw=true "DataFITS Overview")

## Dependencies
- Install Fast Map Matching (follow instructions on https://github.com/cyang-kth/fmm)
  - Please note that FMM was developed in Python 2, there is a workaround for Python 3 
- Install all python requirements
```shell
pip3 install -r requirements.txt
```

## Usage
### Data Acquisition
- Clone the repository and open the script *main_acquisition.py* to define the cities for which you want to collect the data;
- Set the acquisition frequency and sources in the configuration file (*config.ini*)
- Run *main_acquisition.py* to collect data for all cities from the defined sources
- ENVIROCAR: To collect and process vehicular data, please run *envirocar_main.py* (for all cities defined in *main_acquisition.py*)
### Data Fusion
- *Config.ini*: Use [main-config] to set the city and configure the further data processing
- Run *framework_setup.py*: Initialize the framework
- Switch to the folder *data_enrichment* and run the following scripts as single steps of the framework:
  - ___preparation<span>.py___: Prepares the collected data and parses the input for FMM 
  - ___get_osm_shp.py___: Collects the shapefile of the defined city from OSM
  - ___mapmatching<span>.py___ (Python2): Uses a mapmatching technique (FMM) to map the coordinates from the collected data on a road network
  - ___fmm_output.py___: Fuses the data from mapmatching with the collected data
  - ___label_data.py___: Processes the data for spatiotemporal fusion
- Use the output.csv file of the framework in the folder *data_enrichment/output* to achieve the enriched data

## Data Acquisition

The framework collects traffic related data from different data sources (e.g., Microsoft Bing Maps, HERE, OpenData, ...). The acquistion process can be started with the file ***main_acquisition.py***. 
- The user can specify a time value, which changes the time interval for the acquisition process (default: 10 min).
- The script saves the data to different csv files which are named according to their data source and the acquisiton day.

The following sources and german cities are currently implemented but can be further expanded
- [x] Bonn, Köln, Hamburg, Berlin, München, Bremen, Dortmund, Münster, Mönchengladbach, Düsseldorf, Chemnitz
- [x] HERE Traffic, Incident
- [x] BING Incident
- [x] Weather (Meteostat)
- [x] OpenData (only Bonn and Köln)
- [x] Envirocar (Database)  
- [ ] ADAC

You can access the data for Bonn here: [Bonn Data (December 2021 - August 2022)](http://rettore.com.br/prof/datafits/data/bonn_dec21-aug22.zip)

## Heterogeneous Data

Regarding the different data sources, the script obtains different heterogenous data features. Traffic data from different sources comes with data features like average vehicle speed and a traffic factor with the addition of construction data from other sources. Furthermore, we are collecting vehicular data like CO2 emission or the fuel consumption from the Envirocar database and conclude our acquisition with hourly weather data.
The fusion of this data can further improve the overall quality and quantity of the acquired dataset.

## Fast Map Matching

With a technique called Map Matching, it is possible to match some kind of coordination point or a line of points to a underlying shape file. A shape file contains the road network of a given location, with a ***FID*** value giving each edge of this file (and therefore each road piece) a unique id. 
For this purpose we are using Fast Map Matching (https://github.com/cyang-kth/fmm), solving the following given problems of heterogeneous data:
- Some of the data acquired is not very precise. E.g., Bing Incident Data simply gives the GPS Coordinates of one starting and one end point.
- There could be data from different sources describing the same piece of the road. However, because the location of the road piece is only given by GPS coordinates (Latitude and Longitude) it's not that easy to tell if two data sources are describing the same piece of a road.


### *Preparation*
The data which is acquired contains many features, with data values which are not needed in the process of Fast Map Matching (FMM). FMM needs the following input:
``
0; LINESTRING(Longitude1, Latitude1, Longtiude2, Latitude2, ...) 
``
The first value describes the id of the GPS entry and the second one, separated by a semicolon, is a geometry string in the well-known text format (WKT). The geometry can consist of points (1 GPS coordinate) or Linestrings (multiple GPS coordinates).
The script ***preparation<span>.py*** takes care of this preparation process and converts the originally acquired csv file and converts it to a csv file which can be parsed by the FMM program. For now it just takes all data entries from the first timestamp and converts them to an FMM input file (one file for each source).

### *Shapefile*
To obtain a shapefile, which contains all network edges to a given City or Bounding Box, run ***get_osm_shp.py***. Within the script you can set the BB or the City; however keep in mind: 
- if you do set a new Bounding Box or City, the FID values will change. (E.g. FID:0 in Cologne != FID:0 in Bonn)
- if you obtain the shapefile for the same city or bounding box the FID values stay the same

To obtain the shapefile of a region we are using osmnx (https://github.com/gboeing/osmnx), which can be installed with pip or conda. At this moment the newest version of this tool is not working, but you can install version 0.16.2 via pip as a workaround.
### *Map Matching*
For the FMM process we need the following input files:

- The trip file (output of *prep_fmm.py*) containing the WKT strings for all data entries
- The shapefile (edges.shp) which is used to create the road network on which the linestrings are mapped on
- A .ubodt file. This file can be created with the FMM tool, but it just needs to be created once for the same shapefile and can be loaded in the FMM process.

In the ***mapmatching<span>.py*** script you can furthermore configure the mapmatching with parameters like the search radius r, the number of candidates k and the GPS error.

The output of the FMM contains the following data values:

- id: The id of the data entry/trajectory
- opath array: Contains the fid values of the edges which were matched to each point in the input trajectory
- cpath array: Contains the fid values of the edges of the path traversed by the trajectory
- mgeom: The geometry of the cpath (New, matched GPS coordinates in the WKT format)

Attention:  ***mapmatching<span>.py*** is a python2 script; every other script can be run with python3


### *Output of fmm*
The next two python scripts which are presented take care of the ouput from the FMM tool fusing it with the original aquired data and converting it to json, such that it can be displayed in things like QGIS.

***fmm_output.py***:
This script takes the new obtained data (opath, cpath, new gps coordinates) and inserts them back into the acquired csv file. Furthermore it adds the cpath and opath arrays, such that this new information can be used in following subtasks.
There is also some code wich generates geojson files for each data source regarding the new GPS coordinates. The geojson file can be used as an input for geographic programs like QGIS, visualizing the acquired data together with features like the traffic jam factor or the speed.

***label_data.py***:
The last script extracts the fid values from the data entries and regroups the data by this identifying value. This allows to look at the complete data set by each single road segment, which enriches the overall amount of information. Furthermore, the final data output *data_enrichment/output/output.csv* can be easily grouped in a spatiotemporal way.


## Data Usage ##
### Data Enrichment
An exemplary except of the resulting csv file:

| opath_id   |   id   |  source |   time    | opath | speed | traffic | incidentType | ... |
| :--------: |:------:| :------:|:---------:|:-----:|:--------:|:--------:|:--------:|--------:|
|...|...|...|...|...|...|...|...|...|
|   315| 57| HERE Traffic| 13.07.2021 09:45| [266, 313, 315, ...] |50| 3.1| None | ...
|   315| 1| OpenData Traffic| 13.07.2021 09:45| [265, 311, 315, ...] | 45 |3| None | ...
|   315| 1| Incident Bing| 13.07.2021 09:46| [315, 319] | None | None | Construction | ...
|...|...|...|...|...|...|...|...|...|
|   1274| 25| Incident Bing| 13.07.2021 09:46| [1274, 3005] | None | None | Miscellaneous | ...
|   1274| 9| Incident HERE| 13.07.2021 09:45| [843, 1274, 2684, ...] | None | None | Accident | ...

- opath_id describes the fid of the shapefile
- id gives the id of the data entry respectively to the source
- source contains the data source
- time: The timestamp of the data acquisition
- opath: The original opath array of the FMM process
- features: All features which were in the original acquired data file are listed as single columns

This file gives more information to every road piece which is covered by our initial data, as it fuses data from different data sources together and uses mapmatching to make sure, they are describing the same road piece. 
It can be used to fuse heterogeneous data from different sources but with the same spatial time aspect or it can give better information about the current situation.

### Data Analysis & Visualization
We used the enriched data to create some statistics and visualizations using the programming language R. The used scripts are going to be added to this repository at a later point in time.
You can find an excerpt of some visualizations here, please see [Data Characterization](data_characterization/README.md) for more details.

![Alt text](img/02Envirocar_Accident%2BRoadHazard.svg?raw=true "Heatmap speed and incident")

Heatmap showing vehicular speed and incident reports

![Alt text](img/jf_speed.svg?raw=true "Heatmap speed and incident")

Average vehicle speed under different traffic conditions

How to cite
----
If you decided to use this framework, please, refer to it as:

-  Philipp Zissner, Rettore, Paulo H. L., Bruno P. Santos, Roberto Rigolin F. Lopes, and Peter Sevenich.
Road traffic density estimation based on heterogeneous data fusion. In IEEE Symposium on Computers
and Communications (ISCC), Rhodes Island, Greece, June 2022

Publications
----

- Philipp Zissner, Rettore, Paulo H. L., Bruno P. Santos, Roberto Rigolin F. Lopes, and Peter Sevenich.
Road traffic density estimation based on heterogeneous data fusion. In IEEE Symposium on Computers
and Communications (ISCC), Rhodes Island, Greece, June 2022


Contacts
----

paulo.lopes.rettore@fkie.fraunhofer.de

philipp.zissner@fkie.fraunhofer.de

License
----

GPL