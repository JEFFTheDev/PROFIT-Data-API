import xml.etree.ElementTree as ET

import urllib3
import time
from bs4 import BeautifulSoup, SoupStrainer
import csv
import profitdateparser as dp


class Event:

    def __init__(self, name, date, location):
        self.name = name
        self.date = date
        self.location = location


# retrieve al attribute definitions from xml file
tree = ET.parse('scrape_definitions/vvv_zeeland.xml')
root = tree.getroot()

event_attributes = root.find('event')
attr_list = root.findall('event')[0]
event_name = attr_list.find('name').text
date = attr_list.find('date').text
# type_event = attr_list.find('type').text
location = attr_list.find('location').text
data_container = root.find('data_container').text
url = root.find('url').text
known_date = None


def get_events_from_page(page_url):
    # gets html from a page
    page_data = get_page_data(page_url)
    event_soup_list = list(BeautifulSoup(page_data, features="lxml", parse_only=SoupStrainer(class_=data_container)))

    processed_events = []

    for event in event_soup_list:
        event_values = dict()

        for event_field in event_attributes:
            position = int(event_field.attrib["position"])
            event_soup = BeautifulSoup(str(event), features="lxml")
            possible_values = event_soup.findAll(attrs={'class': event_field.text}, recursive=True)

            if not len(possible_values) <= position:
                event_values[event_field.tag] = possible_values[position].get_text().strip()

        if "date" in event_values and "name" in event_values and "location" in event_values:
            if event_values["date"] != '' and not dp.contains_blacklisted_phrases(event_values["date"]):
                processed_event = Event(event_values["name"], dp.parse(event_values["date"]), event_values["location"])
                processed_events.append(processed_event)

    return processed_events


# continuously retrieve html data from website pages and make event objects out of it
def scrape_all(url, time_out_time):
    full_event_list = []

    x = 1
    number_of_pages = 34
    while x != number_of_pages:
        # add ?p parameter to url to request data from next page
        new_url = url + "?p=" + str(x)

        page_events = get_events_from_page(new_url)
        full_event_list += page_events
        x += 1
        print(new_url)

        # sleep the thread to prevent sending to many requests in to short of a time
        time.sleep(time_out_time)

    print("Retrieved: " + str(len(full_event_list)) + " events")

    return full_event_list


# sends a request to url parameter and returns html result as a string
def get_page_data(url):
    hdr = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'}

    html_string = urllib3.PoolManager().request("GET", url, headers=hdr)
    return html_string.data


# # Scrape from VVV Zeeland
event_list = scrape_all(url, 1)

# Write events to csv file
# with open('events.csv', 'w+', newline='') as csvfile:
#     reader = csv.reader(csvfile, quotechar='|')
#     writer = csv.DictWriter(csvfile, fieldnames=['Name', 'Date', 'Location'])
#     writer.writeheader()
#     for e in event_list:
#         writer.writerow({'Name': e.name, 'Date': e.date, 'Location': e.location})
