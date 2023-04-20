# Traffic Data Characterization

This file shows a characterization of the traffic data from the city of Bonn.
The traffic is described through four unique levels, representing
low (0-1), normal (>1 - 4), increased (>4 - 7) and jammed
traffic (>7 - 10). Furthermore, the streets are grouped into
motorways (speed limit: > 100 km/h or none), main roads (fast roads,
speed limit: 50 km/h - 100 km/h) and residential (small roads in 
living areas, speed limit: 30 km/h to 5 km/h). 

## Traffic Overview

First, we provide some general traffic-related statistics that
are given in the table below. It provides the number of data entries for
each traffic level on the different street types, including 
information about the average traffic, speed and relative speed 
(:= driven speed / speed limit).
Based on this analysis, there is a similar distribution of traffic,
with the highest proportion of entries given in a low traffic state.
However, there is a noticeable difference between the distributions 
related to the different street types. Similarly, there are
significant differences related to the average traffic and 
speed values.

<table>
    <thead>
        <tr>
            <th>Traffic Level</th>
            <th>Street Type</th>
            <th>Entries</th>
            <th>Traffic</th>
            <th>Speed</th>
            <th>Speed (rel.)</th>
        </tr>
        <tr>
            <td>Low (1) <br> Normal (4) <br> Increased (7) <br> Jammed (10)</td>
            <td>Main Road <br> Main Road <br> Main Road <br> Main Road</td>
            <td align="right">2,670,574 (80.85%) <br> 527,150 (15.96%) <br> 61,169 (01.85%) <br> 44,047 (01.33%)</td>
            <td align="right">0.86 <br> 2.21 <br> 5.07 <br> 9.79</td>
            <td align="right">37.74 <br> 31.88 <br> 17.68 <br> 15.37</td>
            <td align="right">68.60% <br> 56.64% <br> 32.11% <br> 30.72%</td>
        </tr>
        <tr>
            <td>Low (1) <br> Normal (4) <br> Increased (7) <br> Jammed (10)</td>
            <td>Motorway <br> Motorway <br> Motorway <br> Motorway</td>
            <td align="right">2,029,821 (80.50%) <br> 269,694 (11.77%) <br> 166,481 (06.60%) <br> 28,64 (01.14%)</td>
            <td align="right">0.41 <br> 2.11 <br> 4.91 <br> 8.74</td>
            <td align="right">83.79 <br> 79.72 <br> 53.78 <br> 27.42</td>
            <td align="right">86.86% <br> 80.77% <br> 57.27% <br> 28.67%</td>
        </tr>
        <tr>
            <td>Low (1) <br> Normal (4) <br> Increased (7) <br> Jammed (10)</td>
            <td>Residential <br> Residential <br> Residential <br> Residential</td>
            <td align="right">286,654 (93.68%) <br> 285 (00.09%) <br> 16,218 (05.20%) <br> 3,062 (00.98%)</td>
            <td align="right">0.88 <br> 2.27 <br> 5.00 <br> 10.00</td>
            <td align="right">27.04 <br> 13.76 <br> 13.26 <br> 3.31</td>
            <td align="right">53.93% <br> 27.85% <br> 27.05% <br> 03.36%</td>
        </tr>
    </thead>
</table>

Figure 1 shows the distribution of traffic levels regarding
the aspect of time, again for different street types. The
_Morning_ is defined from 5 a.m. to 12 p.m, _Afternoon_ from
12 p.m. to 5 p.m., _Evening_ from 5 p.m. to 9 p.m. and
_Night_ from 9 p.m. to 5 a.m.  
Noticeably, the highest proportion of data entries 
represents a low traffic level of one, but there is a 
significant difference in the distribution of traffic levels
between the different street times. Furthermore, the traffic 
is correlated to the time of the day, as there is a 
higher level of traffic during the morning and afternoon, 
compared to the evening and night.

<figure>    
    <img width="80%"
    src="img/traf_streets+timeofday.png"
    alt="Traffic based on street type and time of day">
    <figcaption> Figure 1: Distribution of traffic based on street type and time of the day</figcaption>
</figure>

Next, the relation between the relative driven speed and 
traffic level on the different street types is analysed,
as shown in Figure 2. It shows the traffic level on the
x-axis, relative speed on the left y-axis and traffic 
value on the right y-axis. There is a strong correlation
between both traffic features with a varying level of 
dependency according to the different street types. This 
clearly shows an inverse correlation between these two 
traffic features, but additionally states that the level 
of correlation significantly differs between the depicted 
street types.

<figure>    
    <img width="80%"
    src="img/traf_streets_speed.png"
    alt="Relation of speed and traffic based on street types">
    <figcaption> Figure 2: Relation of speed and traffic on different street types</figcaption>
</figure>


## Spatiotemporal Visualization

The following figures support the analysis of information 
regarding a spatiotemporal aspect. 

Figure 3 depicts the data coverage of different street types
and highlights all covered road segments by their average
speed value. As visible, motorways provide a close to
perfect coverage in the discussed area, as it is the most
important road type used for transportation. Main roads
show a significant lower coverage of information and a 
reduction of the average speed value. In contrast, only a
very small subset of residential streets is covered by the
dataset. A visualization like this helps to identify 
problematic traffic areas that show a low data coverage and
can be used to further investigate road segments that have 
a very low average speed, indicating high traffic.

<figure>    
    <img width="80%"
    src="img/traf_geo_streets_speed2.png"
    alt="Street coverage and relative speed">
    <figcaption> Figure 3: Street coverage and relative speed of each road segment</figcaption>
</figure>

Finally, the traffic during different times of the day 
is presented in Figure 4, showing differences between 
certain areas. During the night and evening, the traffic
level is low on all locations, except a few roads close
to the city center and motorway parts that show a slightly
increased traffic. In contrast, during the morning and 
afternoon, multiple road segments show higher traffic 
values, especially main roads in the center. This figure
visualizes the spatiotemporal dependency of traffic values,
by showing the spatially differing change of traffic 
during time.

<figure>    
    <img width="80%"
    src="img/traf_by_time2.png"
    alt="Street coverage and relative speed">
    <figcaption> Figure 4: Spatiotemporal traffic view</figcaption>
</figure>