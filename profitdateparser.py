import dateparser
import xml.etree.ElementTree as ET
import re


tree = ET.parse('date_definitions/date_rules.xml')
root = tree.getroot()
blacklist = tree.find('blacklisted_phrases')
unparsable_phrases = tree.find('unparsable_phrases')


def parse(date):
    parsable_date = remove_unparsable_phrases(date)
    parsed_date = dateparser.parse(parsable_date)
    return parsed_date


def contains_blacklisted_phrases(date):
    for phrase in blacklist:
        if re.search(phrase.text, str(date), re.IGNORECASE):
            return True
    return False


def remove_unparsable_phrases(date):
    for phrase in unparsable_phrases:
        pattern = re.compile(phrase.text, re.IGNORECASE)
        pattern.sub("", str(date))
    return str(date)
