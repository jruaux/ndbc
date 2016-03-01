#!/usr/bin/env python
from datetime import datetime
import sys, json, pytz, buoyant, logging

from splunklib.modularinput import Script, Scheme, Argument, Event


def getepoch(dt_with_tz):
    return (dt_with_tz - datetime(1970, 1, 1, tzinfo=pytz.utc)).total_seconds()

def getmap(obs):
    obsmap = {}
    if hasattr(obs, 'id'):
        obsmap['station'] = obs.id
    if hasattr(obs, 'datetime'):
        obsmap['datetime'] = obs.datetime.isoformat()
    names = ['url', 'name', 'lat', 'lon', 'units', 'meta']
    names.extend(buoyant.buoy.NAMES.values())
    for name in names:
        if (hasattr(obs, name)):
            obsmap[name] = getattr(obs, name)
    return obsmap

class NDBCScript(Script):
    def get_scheme(self):
        scheme = Scheme("NDBC")
        scheme.description = "Streams NDBC station events."
        scheme.use_external_validation = True
        stations_argument = Argument("stations")
        stations_argument.title = "Station IDs"
        stations_argument.data_type = Argument.data_type_string
        stations_argument.description = "List of station IDs separated by a space"
        stations_argument.required_on_create = True
        scheme.add_argument(stations_argument)
        return scheme

    def validate_input(self, validation_definition):
        stations = validation_definition.parameters["stations"].split(" ")
        for station in stations:
            obs = buoyant.Buoy(station)
            for k, v in obs.xml.attributes.items():
                if k == 'id' and v == '':
                        raise ValueError("Problem accessing NDBC station " + station)

    def stream_events(self, inputs, ew):
        for input_name, input_item in inputs.inputs.iteritems():
            stations = input_item["stations"].split(" ")
            for station in stations:
                try:
                    obs = buoyant.Buoy(station)
                    event = Event()
                    event.stanza = input_name
                    event.data = json.dumps(getmap(obs))
                    if hasattr(obs, 'datetime'):
                        event.time = getepoch(obs.datetime)
                    ew.write_event(event)
                except Exception:
                    logging.exception('Connect timeout for station %s', station)

if __name__ == "__main__":
#     stations = "13010 15001 15006 15002 31007 31006 31001 13001 31005 31002 13009 41026 13008 31004 31003"
#     for station in stations.split(" "):
#         obs = buoyant.Buoy(station)
#         obsmap = getmap(obs)
#         print(json.dumps(obsmap))
    sys.exit(NDBCScript().run(sys.argv))
