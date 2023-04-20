# General Data Statistics

This file shows a data characterization for the German city Bonn, providing
an exemplary use case for the proposed fused dataset. First, we share some
information about the acquired data and the contained data types. 

The data characterization is split into two parts characterizing the 
[Traffic](traffic_data/README.md) and [Incident](incident_data/README.md) information. This analysis 
reflects a data time frame of 9 months, from December 2021 to August 2022.


## Data Sources

<table>
    <thead>
        <tr>
            <th>Source</th>
            <th>Type</th>
            <th>Data Features</th>
            <th>Entries</th>
        </tr>
        <tr>
            <td><a href="https://developer.here.com/documentation/traffic/dev_guide/topics_v6.1/example-flow-intro.html">Traffic HERE</a></td>
            <td>Commercial</td>
            <td>Speed <br> Traffic <br> Street <br> GPS <br> etc.</td>
            <td align="right">6,038,496</td>
        </tr>
        <tr>
            <td><a href="https://opendata.bonn.de/dataset/stra%C3%9Fenverkehrslage-realtime">Traffic OD</a></td>
            <td>Open</td>
            <td>Speed <br> Traffic <br> GPS</td>
            <td align="right">3,852,144</td>
        </tr>
        <tr>
            <td><a href="https://developer.here.com/documentation/traffic/dev_guide/topics/example-incidents-intro.html">Incident HERE</a></td>
            <td>Commercial</td>
            <td>Inc. Type <br> Description <br> GPS <br> Criticality <br> etc.</td>
            <td align="right">949,709</td>
        </tr>
        <tr>
            <td><a href="https://learn.microsoft.com/en-us/bingmaps/rest-services/traffic/get-traffic-incidents">Incident BING</a></td>
            <td>Commercial</td>
            <td>Inc. Type <br> Description <br> GPS <br> etc.</td>
            <td align="right">1,876,353</td>
        </tr>
        <tr>
            <td><a href="https://opendata.bonn.de/dataset/baustellen-tagesaktuell-mit-ortsangabe-bonn">Incident OD</a></td>
            <td>Open</td>
            <td>Inc. Type <br> Description <br> GPS <br> etc.</td>
            <td align="right">957,398</td>
        </tr>
        <tr>
            <td><a href="https://envirocar.org/?lng=en">Envirocar</a></td>
            <td>Open</td>
            <td>Speed <br> Fuel Consumption <br> CO2 emission <br> RPM <br> etc.</td>
            <td align="right">9,917</td>
        <tr>
            <td><a href="https://dev.meteostat.net/">Meteostat</a></td>
            <td>Open</td>
            <td>Weather condition <br> Temperature <br> Precipitation <br> etc.</td>
            <td align="right">6,576</td>
        </tr>
</table>


## Data Coverage
The table below presents the data coverage for each individual data source, by showing the amount of total and unique roads.
Moreover, it states the proportion of data that is added to the fused dataset and includes the number roads that show overlapping
data from multiple sources, showing the benefits of data fusion.

![Alt text](../img/Coverage_Sources.PNG?raw=true "Road segment coverage")

Table showing the covered road segments by each data source



