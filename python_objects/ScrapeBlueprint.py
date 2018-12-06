from xml.etree.ElementTree import parse


class EventBlueprint:

    def __init__(self, scrape_definitions_xml):
        xml_root = parse(scrape_definitions_xml).getroot()
        attr_list = xml_root.findall('event')[0]

        self.event_class = xml_root.find('event').attrib["class"]

        self.name_class = attr_list.find('name').attrib["class"]
        self.name_position = int(attr_list.find('name').attrib["position"])

        self.date_class = attr_list.find('date').attrib["class"]
        self.date_position = int(attr_list.find('date').attrib["position"])

        self.location_class = attr_list.find('location').attrib["class"]
        self.location_position = int(attr_list.find('location').attrib["position"])

        self.url = xml_root.find('site').attrib["url"]
        self.url_page_indicator = xml_root.find('site').attrib["pageIndicator"]
