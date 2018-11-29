import re
import xml.etree.ElementTree as ET
from datetime import *

import dateparser

tree = ET.parse('dateformatting/date_rules.xml')
root = tree.getroot()
blacklist = tree.find('blacklisted_phrases')
unparsable_phrases = tree.find('unparsable_phrases')

years_passed = 0


def parse(date: str) -> datetime:
    parsable_date = remove_unparsable_phrases(date)
    parsed_date = dateparser.parse(parsable_date)

    return parsed_date


def is_blacklisted(date: str):
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
    # date_to_guess = date_to_guess.replace(year=known_date.year)

    # date to guess is always in the same year as known year, or in the year after
    if date_to_guess < known_date:
        date_to_guess = date_to_guess.replace(year=(known_date.year + 1))

    return date_to_guess
