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
attr_list = root.findall('event')[0]
event_name = attr_list.find('name').text
date = attr_list.find('date').text
type_event = attr_list.find('type').text
location = attr_list.find('location').text
data_container = attr_list.find('data_container').text
url = attr_list.find('url').text


def get_events_from_page(page_url):
    page_data = get_page_data(page_url)

    # make soup of html data with only our divs that contain the events
    soup = BeautifulSoup(page_data, features="lxml", parse_only=SoupStrainer(class_=data_container))
    attributes = [event_name, date, location]
    soup_list = list(soup)
    all_events = []

    known_date = None

    for item in soup_list:
        new_s = BeautifulSoup(str(item), features="lxml")

        all_attr = []
        for attr in attributes:
            attribute = new_s.findAll(attrs={'class': attr}, recursive=True)
            actual_attr = ''

            for a in attribute:
                actual_attr += a.get_text()

            # hardcoded solution to remove type from location string
            actual_attr = actual_attr.replace('evenement', '')
            actual_attr = actual_attr.replace('tentoonstelling', '')
            actual_attr = actual_attr.replace('excursie', '')

            all_attr.append(' '.join(actual_attr.split()))

        name = all_attr[0]
        event_date = all_attr[1]
        loc = all_attr[2]

        if event_date != '' and not dp.contains_blacklisted_phrases(event_date):
            if known_date is not None:
                parsed_date = dp.guess_year(known_date, dp.parse(event_date))
                known_date = parsed_date
            else:
                known_date = dp.parse(event_date)
                parsed_date = known_date

            all_events.append(Event(name, parsed_date, loc))

    return all_events


# continuously retrieve html data from website pages and make event objects out of it
def scrape_all_by_timer(url, timer):
    full_event_list = []

    x = 1
    number_of_pages = 33
    while x != number_of_pages:

        # add ?p parameter to url to request data from next page
        new_url = url + "?p=" + str(x)
        page_events = get_events_from_page(new_url)
        full_event_list += page_events
        x += 1
        print(new_url)

        # sleep the thread to prevent sending to many requests in to short of a time
        time.sleep(timer)

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


# Scrape from VVV Zeeland
event_list = scrape_all_by_timer(url, 1)

# Write events to csv file
with open('events.csv', 'w+', newline='') as csvfile:
    reader = csv.reader(csvfile, quotechar='|')
    writer = csv.DictWriter(csvfile, fieldnames=['Name', 'Date', 'Location'])
    writer.writeheader()
    for e in event_list:
        writer.writerow({'Name': e.name, 'Date': e.date, 'Location': e.location})




