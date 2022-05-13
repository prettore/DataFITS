'''
Web crawler to get traffic data from ADAC page
'''
import datetime
import os
import re
import threading
import urllib.request
from bs4 import BeautifulSoup
import pandas as pd
import time
import logging


old_traffic_html = []

def acquire_data(html, page_no):
    global old_traffic_html, times, art_of_msg, descriptions, optional_information, road_no, intersection
    i = 0
    information = []
    street_names = []
    current_street_names = []
    intersections = []
    traffic_html = []
    entries_this_page = []
    entries_last_page = []
    #traffic_news = html.find("div", {"data-testid":"VM-results"})
    
    traffic_html = html.find_all("div",{"data-testid":"VM-news-item"})
    #print(len(traffic_html))

    if len(traffic_html) == 0:
        return False

    for i in range (len(traffic_html)):
        #print(f"test --- ::::: {traffic_html[i]}")
  
        if page_no > 1:
            if traffic_html == old_traffic_html:
                return False
        old_traffic_html = traffic_html
        if page_no > 1 and len(traffic_html) < 10:
            return False
        #print(traffic_html)
        time_obj = datetime.datetime.utcnow()
        times.append(time_obj)
        art_of_msg.append(traffic_html[i].img["alt"])
        #traffic_html = html.find_all('div', class_="sc-bHKNvF kgmPeX")
        #art_of_msg.append(news.img["alt"])  #Contains the type of message [Verkehrsmeldung, Vollsperrung, Stau]
        for entry in traffic_html[i].div:
            information.append(entry.text.replace("\xa0",""))  #Contains all the given information
        #print(str(art_of_msg[i]) + str(information))
        
        #print(information)
        current_street_names.append(information[0])
        street_names.append(information[0])
        descriptions.append(information[1])
        if (len(information) == 3):
            optional_information.append(information[2:])
        else:
            optional_information.append("None")
        information = []
        for entry in current_street_names:
            number = re.findall(r'^[a-zA-Z]*\d*',entry)
            if "" in number:
                number = ["X"]
            #print(number)
            
            try:
                if len(number) > 0:
                    intersections = re.findall(r'[a-zA-Z][^A-Z]*',entry[len(number[0]):])
                    #print(intersections)
                    if (number[0][0].isalpha()):
                        road_no.append(number[0]) #checks if there is a alphabetical char in the road name
                        if len(intersections) > 1 and intersections[0].isalpha():
                            intersection.append(intersections[0].split(" ")[0]+" -- "+intersections[1].split(" ")[0])
                        else:
                            intersection.append(entry[len(number[0]):]) #Adds all other roads than highways (there is only one location and no intersection between 2)
                    else:
                        road_no.append("A"+number[0]) #adds the A for Autobahn
                        if len(intersections) > 1:
                            intersection.append(intersections[0].split(" ")[0]+" -- "+intersections[1].split(" ")[0]) #Adds the 2 locations from the highway intersection
                        else:
                            intersection.append(intersections[0].split(" ")[0])
                else:
                    road_no.append("?")
                    intersection.append(entry)
            except IndexError:
                logging.error("There was an error with the following data " + entry)
            current_street_names = []
        i += 1
    return True


def check_for_data(location_name, timeWaiting, distance_val, Construction_Sites, searchType):

    page_no = 1

    while True:

        response = ""
        '''
        ' The data for e.g., NRW is completely correct.
        ' The data for germany contains many duplicates, 
        '''

        #Web URL
        #url = "https://www.adac.de/verkehr/verkehrsinformationen/de/nordrhein-westfalen/?country=D&federalState=NW&street=&streetType=Highway&showTrafficNews=true&showConstructionSites=false&pageNumber="+str(page_no)+"&submit=true"
        region_url = "https://www.adac.de/verkehr/verkehrsinformationen/de/?country=D&federalState=&street=&streetType=Highway&showTrafficNews=true&showConstructionSites=false&pageNumber="+str(page_no)+"&submit=true"
        
        city_url = "https://www.adac.de/verkehr/verkehrsinformationen/de/?locationName="+location_name+"&distance="+str(distance_val)+"&showTrafficNews=true&showConstructionSites=" + Construction_Sites + "&submit=true&pageNumber="+ str(page_no) +"&query=" + location_name
        #Get request
        if searchType == "region":
            search_url = region_url
        elif searchType == "city":
            search_url = city_url
        #req = urllib.request.Request(search_url, data=None, timeout=10)
        try:
            response = urllib.request.urlopen(search_url, timeout = 10)
            #parse BeautifulSoup html doc 
            html = BeautifulSoup(response.read(), 'html.parser')
            print("--------------"+str(search_url)+"------------")
            if (acquire_data(html, page_no) == False):
                break

            page_no+=1  #The page number on the website is capped at 10, but there are more pages after that
        except:
            print("ERROR: No connection to ADAC possible")
            logging.error("Connection Problem with ADAC service")
            return 

    timestr = datetime.datetime.utcnow().strftime("%Y%m%d")

    #print(len(times),len(art_of_msg),len(road_no),len(intersection),len(descriptions),len(optional_information))
    try:
        df = pd.DataFrame({'Timestamp':times,'Art':art_of_msg[:],'Road No':road_no[:],'Intersection':intersection[:],'Desc':descriptions[:],'Further Information':optional_information[:]}).sort_values(by=['Road No'])
        df.drop_duplicates(["Road No", "Intersection", "Desc"], keep="first", inplace=True)

        if not os.path.isfile("./"+location_name+"/ADAC/out_adac"+timestr+".csv"):
            HEADER_VAL = True
            WRITE_MODE = "w+"
        else:
            HEADER_VAL = False
            WRITE_MODE = "a"
        df.to_csv("./"+location_name+"/ADAC/out_adac"+ timestr +".csv",index=False,encoding="utf-8", mode=WRITE_MODE, header=HEADER_VAL)
        logging.info(location_name+": ADAC Data acquired and saved; Found " + str(df.shape[0]) + " data entries")
    #print(df)
    except Exception as e:
        logging.error(e)
        logging.debug(f"Time: {len(times)}, Art: {len(art_of_msg)}, Road_No: {len(road_no)}, Intersection: {len(intersection)}, \
            Description: {len(descriptions)}, OptionalInfo: {len(optional_information)}")

        #logging.error(len(times),len(art_of_msg),len(road_no),len(intersection),len(descriptions),len(optional_information))
    return True

times = []
art_of_msg = []
descriptions = []
optional_information = []
road_no = []
intersection = []

def main(city_list, timeWaiting, logging_lvl):
    #threading.Timer((timeWaiting*60), main, [location_name, timeWaiting, logging_lvl]).start()
    global times, art_of_msg, descriptions, optional_information, road_no, intersection
    logging.basicConfig(filename='logfile.log', level=logging_lvl, format='%(asctime)s, %(levelname)s %(message)s',datefmt='%Y-%m-%d,%H:%M:%S')
    for city in city_list:
        times = []
        art_of_msg = []
        descriptions = []
        optional_information = []
        road_no = []
        intersection = []
        if (os.path.isdir('./'+city+'/') == False):
            os.makedirs('./'+city+'/')    #Creates the envirocar folder to save the data
        if (os.path.isdir('./'+city+'/ADAC/') == False):
            os.makedirs('./'+city+'/ADAC')
        check_for_data(city, timeWaiting, distance_val = 25, Construction_Sites = "false", searchType="city")


if __name__=="__main__":
    main(city_list = ["bonn","koeln","hamburg","berlin","muenster","moenchengladbach","duesseldorf","muenchen","stuttgart","dortmund","bremen","chemnitz"], timeWaiting=10, logging_lvl=logging.INFO)