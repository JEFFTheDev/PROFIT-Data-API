from datetime import *
from dateutil.relativedelta import relativedelta

import dateparser
import xml.etree.ElementTree as ET
import re


tree = ET.parse('date_definitions/date_rules.xml')
root = tree.getroot()
blacklist = tree.find('blacklisted_phrases')
unparsable_phrases = tree.find('unparsable_phrases')


def parse(date: str) -> datetime:
    parsable_date = remove_unparsable_phrases(date)
    parsed_date = dateparser.parse(parsable_date)

    return parsed_date


def contains_blacklisted_phrases(date: str):
    for phrase in blacklist:
        if re.search(phrase.text, str(date), re.IGNORECASE):
            return True
    return False


def remove_unparsable_phrases(date: str):
    for phrase in unparsable_phrases:
        pattern = re.compile(phrase.text, re.IGNORECASE)
        pattern.sub("", str(date))
    return str(date)


""" 
This function guesses the year a date should take place in based on
a known date that occurs within a year of the date that will be guessed
it returns the guessed date.
"""


def guess_year(known_date: datetime, date_to_guess: datetime) -> datetime:
    delta_years = known_date.year - date_to_guess.year
    date_to_guess += relativedelta(years=delta_years)

    # date to guess is always in the same year as known year, or in the year after
    if date_to_guess < known_date:
        date_to_guess += relativedelta(years=1)
        print("jaar had moeten veranderen")

    return date_to_guess
