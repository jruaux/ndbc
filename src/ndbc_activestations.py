#!/usr/bin/env python
import sys, requests, json

from splunklib.modularinput import Script, Scheme
from splunklib.modularinput.event import Event

import xml.etree.ElementTree as ET


ENDPOINT = "http://www.ndbc.noaa.gov/activestations.xml"

class ActiveStationsScript(Script):
    
    def get_scheme(self):
        scheme = Scheme("NDBC Active Stations")
        scheme.description = "Fetches list of active NDBC stations."
        scheme.use_external_validation = True
        return scheme

    def validate_input(self, validation_definition):
        return

    def stream_events(self, inputs, ew):
        for input_name, input_item in inputs.inputs.iteritems():
            xmlstring = requests.get(ENDPOINT).content
            root = ET.fromstring(xmlstring)
            time = root.get('created')
            stations = root.findall('station')
            for station in stations:
                data = dict()
                data['time'] = time
                for name in station.attrib:
                    value = station.get(name)
                    if name == 'elev' or name == 'lat' or name == 'lon':
                        value = float(value)
                    data[name] = value
                event = Event()
                event.stanza = input_name
                event.data = json.dumps(data)
                ew.write_event(event)

if __name__ == "__main__":
    sys.exit(ActiveStationsScript().run(sys.argv))
