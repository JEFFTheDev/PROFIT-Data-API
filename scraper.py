import xml.etree.ElementTree as ET
import urllib3
import time
from bs4 import BeautifulSoup, SoupStrainer


class Event:

    def __init__(self, name, date, location):
        self.name = name
        self.date = date
        self.location = location


tree = ET.parse('xml_files/vvv_zeeland.xml')
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
    soup = BeautifulSoup(page_data, features="lxml", parse_only=SoupStrainer(class_=data_container))
    attributes = [event_name, date, location]
    soup_list = list(soup)
    all_events = []

    for item in soup_list:
        new_s = BeautifulSoup(str(item), features="lxml")

        all_attr = []

        for attr in attributes:
            attribute = new_s.findAll(attrs={'class': attr}, recursive=True)
            actual_attr = ''

            for a in attribute:
                actual_attr += a.get_text().replace(" ", "").replace("\n", "")

            # hardcoded solution to remove type from location string
            actual_attr = actual_attr.replace('evenement','')
            actual_attr = actual_attr.replace('tentoonstelling', '')
            actual_attr = actual_attr.replace('excursie', '')

            all_attr.append(actual_attr.strip())

        name = all_attr[0]
        event_date = all_attr[1]
        loc = all_attr[2]

        if name != '':
            all_events.append(Event(name, event_date, loc))

    return all_events


def scrape_all_by_timer(url, timer):
    full_event_list = []

    x = 1
    while x !=39:
        new_url = url + "?p=" + str(x)
        page_events = get_events_from_page(new_url)
        full_event_list += page_events
        x += 1
        print(new_url)
        # print(page_events[1].name)
        time.sleep(timer)

    for event in full_event_list:
        print("Event name: " + event.name)

    print(str(len(full_event_list)))

    return full_event_list


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


event_list = scrape_all_by_timer(url, 2)

event_file = open("events.txt", "w+")

for e in event_list:
    event_file.write(
        "Name: " + e.name + "\n" + "Date: " + e.date + "\n" + "Location: " + e.location + "\n\n")

event_file.close()
