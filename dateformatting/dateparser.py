import re
import xml.etree.ElementTree as ET
from datetime import *

import dateparser

tree = ET.parse('dateformatting/date_rules.xml')
blacklist = tree.find('blacklisted_phrases')
unparsable_phrases = tree.find('unparsable_phrases')


def parse(date_to_parse: str) -> datetime:
    parsable_date = remove_unparsable_phrases(date_to_parse)
    parsed_date = dateparser.parse(parsable_date)

    return parsed_date


def is_blacklisted(date_to_check: str):
    for phrase in blacklist:
        if re.search(phrase.text, str(date_to_check), re.IGNORECASE):
            return True
    return False


def remove_unparsable_phrases(date_to_edit: str):
    for phrase in unparsable_phrases:
        pattern = re.compile(phrase.text, re.IGNORECASE)
        pattern.sub("", str(date_to_edit))
    return str(date_to_edit)


def change_date_to_future(date_to_change: datetime) -> datetime:
    """" If a date is set in the past this method will change it to the next time that day + month
    is set in the future

    e.g. if today is six december 2018  and date is the first of january 2018 it will be changed to
    the first of january 2019"""
    return date_to_change.replace(year=(date_to_change.year + 1)) if date_to_change < datetime.now() \
        else date_to_change
