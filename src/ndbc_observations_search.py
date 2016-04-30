#!/usr/bin/env python

import json, sys, requests

from splunklib.modularinput import Script, Scheme
from splunklib.modularinput.argument import Argument
from splunklib.modularinput.event import Event

import xml.etree.ElementTree as ET
from ndbc_observations import get_dict


ENDPOINT = "http://www.ndbc.noaa.gov/rss/ndbc_obs_search.php?lat={lat}&lon={lon}&radius={radius}"

class ObservationsSearchScript(Script):
    
    def get_scheme(self):
        scheme = Scheme("NDBC Observations Search")
        scheme.description = "Streams observation events from nearby NDBC stations."
        scheme.use_external_validation = True
        latitude_argument = Argument("latitude")
        latitude_argument.title = "Latitude"
        latitude_argument.data_type = Argument.data_type_number
        latitude_argument.description = "Latitude of the center of the search area"
        latitude_argument.required_on_create = True
        scheme.add_argument(latitude_argument)
        longitude_argument = Argument("longitude")
        longitude_argument.title = "Longitude"
        longitude_argument.data_type = Argument.data_type_number
        longitude_argument.description = "Longitude of the center of the search area"
        longitude_argument.required_on_create = True
        scheme.add_argument(longitude_argument)
        radius_argument = Argument("radius")
        radius_argument.title = "Radius"
        radius_argument.data_type = Argument.data_type_number
        radius_argument.description = "Radius in miles of the search area"
        radius_argument.required_on_create = True
        scheme.add_argument(radius_argument)        
        return scheme

    def validate_input(self, validation_definition):
        lat = validation_definition.parameters["latitude"]
        try:
            float(lat)
        except:
            raise ValueError("Latitude should be a number: " + lat)
        lon = validation_definition.parameters["longitude"]
        try:
            float(lon)
        except:
            raise ValueError("Longitude should be a number: " + lat)
        radius = validation_definition.parameters["radius"]
        try:
            float(radius)
        except:
            raise ValueError("Radius should be a number: " + radius)

    def stream_events(self, inputs, ew):
        for input_name, input_item in inputs.inputs.iteritems():
            plat = input_item["latitude"]
            plon = input_item["longitude"]
            pradius = input_item["radius"]
            url = ENDPOINT.format(lat=plat, lon=plon, radius=pradius)
            xmlstring = requests.get(url).content
            root = ET.fromstring(xmlstring)
            items = root.find('channel').findall('item')
            for item in items:
                data = get_dict(item)
                event = Event()
                event.stanza = input_name
                event.sourceType = "ndbc:observations"
                event.data = json.dumps(data)
                ew.write_event(event)

if __name__ == "__main__":
    sys.exit(ObservationsSearchScript().run(sys.argv))
