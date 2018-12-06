from python_objects.Event import Event
from python_objects.ScrapeBlueprint import EventBlueprint

import dateformatting.dateparser as dp
import urllib3
import time
import bs4 as bs
import csv

# retrieve all attribute definitions from xml file
blueprint = EventBlueprint('scrape_definitions/vvv_zeeland.xml')

# flag gets set to true once pages no longer have events on them
scraped_all_pages = False


def find_value_in_soup(soup, html_class, position):
    value = ''

    #  finds all values with matching html class
    possible_values = list(soup.findAll(attrs={'class': html_class}, recursive=True))

    # checks if there are enough results to grab the one at the position you want
    if len(possible_values) > position:
        value = possible_values[position].get_text().strip()

    return None if value is '' else value


def get_events_from_page(page_url):
    # gets html from a page
    page_data = get_page_data(page_url)

    # makes a soup of all event containers
    event_soup = bs.BeautifulSoup(page_data, features="lxml", parse_only=bs.SoupStrainer(class_=blueprint.event_class))

    # list that will be filled with events as they get processed
    processed_events = []

    # checks if there are still events (event_soup will always contain at least 1 item)
    if len(list(event_soup)) == 1:
        global scraped_all_pages
        scraped_all_pages = True
        return processed_events

    # repeat for every event container
    for event in list(event_soup):

        # makes a soup for a single event
        event_soup = bs.BeautifulSoup(str(event), features="lxml")

        name = find_value_in_soup(event_soup, blueprint.name_class, blueprint.name_position)
        date = find_value_in_soup(event_soup, blueprint.date_class, blueprint.date_position)
        location = find_value_in_soup(event_soup, blueprint.location_class, blueprint.location_position)

        # checks if the data is fit to be saved.
        if not None in (name, location, date) and not dp.is_blacklisted(date):
            date = dp.parse(date)
            date = dp.change_date_to_future(date)
            processed_events.append(Event(name, dp.parse(date), location))

    return processed_events


# continuously retrieve html data from website pages and make event objects out of it
def scrape_all(url, page_indicator, time_out_time):
    full_event_list = []

    page = 1
    while not scraped_all_pages:
        new_url = url + page_indicator + str(page)

        page_events = get_events_from_page(new_url)
        full_event_list += page_events
        page += 1
        print(new_url)

        # sleep the thread to prevent sending to many requests in to short of a time
        time.sleep(time_out_time)

    print("Retrieved: " + str(len(full_event_list)) + " events")

    return full_event_list


# sends a request to url parameter and returns html result as a string
def get_page_data(url):
    hdr = {
        'User-Agent':
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'}

    html_string = urllib3.PoolManager().request("GET", url, headers=hdr)
    return html_string.data


# Scrape from VVV Zeeland
event_list = scrape_all(blueprint.url, blueprint.url_page_indicator, 1)

# Write events to csv file
with open('scrape_output/events.csv', 'w+', newline='') as csvfile:
    reader = csv.reader(csvfile, quotechar='|')
    writer = csv.DictWriter(csvfile, fieldnames=['Name', 'Date', 'Location'])
    writer.writeheader()
    for e in event_list:
        writer.writerow({'Name': e.name, 'Date': e.date, 'Location': e.location})
