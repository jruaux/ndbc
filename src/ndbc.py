#!/usr/bin/env python
from datetime import datetime
import sys, json, requests, pytz
from xml.dom.minidom import parseString
from splunklib.modularinput import Script, Scheme, Argument, Event

BASE_URL = 'http://www.ndbc.noaa.gov/'
OBS_ENDPOINT = BASE_URL + 'get_observation_as_xml.php'
STATION_URL = BASE_URL + 'station_page.php?station={id}'

NAMES = {
    'airtemp': 'air_temp',
    'avgperiod': 'average_period',
    'domperiod': 'dominant_period',
    'meanwavedir': 'mean_wave_direction',
    'msg': 'message',
    'watertemp': 'water_temp',
    'waveht': 'wave_height',
    'winddir': 'wind_direction',
    'windgust': 'wind_gust',
    'windspeed': 'wind_speed',
}

TYPES = {
    'airtemp': float,
    'avgperiod': float,
    'dewpoint': float,
    'domperiod': float,
    'lat': float,
    'lon': float,
    'pressure': float,
    'watertemp': float,
    'waveht': float,
    'windgust': float,
    'windspeed': float,
    'winddir': int,
    'meanwavedir': int
}

def get_text(node):
    while node.nodeType == node.ELEMENT_NODE:
        node = node.childNodes[0]
    if node.nodeType == node.TEXT_NODE:
        return node.data

def get_attrs(elem):
    return ((k, v) for k, v in elem.attributes.items())

def _parse(xmlstring):
    try:
        xml = parseString(bytes(xmlstring))
    except TypeError:
        xml = parseString(bytes(xmlstring, 'utf-8'))
    return xml.getElementsByTagName('observation').item(0)

def getxml(stationid):
    xmlstring = requests.get(OBS_ENDPOINT, params={'station': stationid}).text
    return _parse(xmlstring)

def getobs(stationid):
    obs = {}
    obs['url'] = geturl(stationid)
    obs['station_id'] = stationid
    try:
        xml = getxml(stationid)
        setobs(obs, xml)
    except requests.exceptions.ConnectTimeout:
        obs['message'] = "Connect timeout"
    return obs

def geturl(stationid):
    return STATION_URL.format(id=stationid)

def getepoch(dt_string):
    dt = datetime.strptime(dt_string[:-3], '%Y-%m-%dT%H:%M:%S')
    tz = pytz.timezone(dt_string[-3:])
    dt_with_tz = tz.localize(dt)
    return (dt_with_tz - datetime(1970, 1, 1, tzinfo=pytz.utc)).total_seconds()

def setobs(obs, xml):
    for key, value in get_attrs(xml):
        if key != 'id':
            typ = TYPES.get(key, str)
            classkey = NAMES.get(key, key)
            obs[classkey] = typ(value)
    children = [node for node in xml.childNodes if node.nodeType == node.ELEMENT_NODE]
    for child in children:
        if child.nodeType == child.ELEMENT_NODE:
            classkey = NAMES.get(child.tagName, child.tagName)
            typ = TYPES.get(child.tagName, str)
            value = typ(get_text(child))
            obs[classkey] = value
    units, meta = {}, {}
    for node in children:
        attribs = dict(get_attrs(node))
        name = NAMES.get(node.tagName, node.tagName)
        if attribs.get('uom'):
            units[name] = attribs['uom']
            del attribs['uom']
        if len(attribs) > 0:
            meta[name] = attribs
    obs['units'] = units
    obs['meta'] = meta
    return obs

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
            xml = getxml(station)
            for key, value in get_attrs(xml):
                if key == 'id' and value == '':
                        raise ValueError("Problem accessing NDBC station " + station)

    def stream_events(self, inputs, ew):
        for input_name, input_item in inputs.inputs.iteritems():
            stations = input_item["stations"].split(" ")
            for station in stations:
                obs = getobs(station)
                event = Event()
                event.stanza = input_name
                event.data = json.dumps(obs)
                if obs.has_key('datetime'):
                    event.time = getepoch(obs['datetime'])
                ew.write_event(event)

if __name__ == "__main__":
    # stations = "46219 46251 PFXC1 PRJC1 NTBC1 46028 46215 PSLC1 CPXC1 46412 TIXC1 46233 46232 46231 SDBC1 LJAC1 OHBC1 ICAC1 LJPC1 46218 46086 46047 46225 46224 46223 46222 46221 46025 46217 46069 46053 46216 46054 PTGC1 46011 46241 46242"
    # for station in stations.split(" "):
    #    print(json.dumps(getobs(station)))
    sys.exit(NDBCScript().run(sys.argv))
