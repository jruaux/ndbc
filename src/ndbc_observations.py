#!/usr/bin/env python
import json, sys, requests

from splunklib.modularinput import Script, Scheme
from splunklib.modularinput.argument import Argument
from splunklib.modularinput.event import Event

import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup


ENDPOINT = "http://www.ndbc.noaa.gov/data/latest_obs/{id}.rss"

def normalize(name):
    if name[0] == "{":
        return name.split("}")[1]
    else:
        return name

def get_dict(item):
    data = dict()
    title = item.find('title').text
    data['title'] = title
    if title.startswith("Station"):
        data['station'] = title.split(" ")[1]
    data['guid'] = item.find('guid').text
    data['link'] = item.find('link').text
    soup = BeautifulSoup(item.find('description').text, 'html.parser')
    lines = soup.get_text().splitlines()
    data['time'] = lines[1]
    for i in range(2, len(lines)):
        name, value = lines[i].split(': ')
        if name=="Location":
            location = value.split(" ")
            latitude = float(location[0][:-1])
            if location[0][-1]=='S':
                latitude = -latitude
            longitude = float(location[1][:-1])
            if location[1][-1]=='W':
                longitude = -longitude
            data['lat'] = latitude
            data['lon'] = longitude
            data['location'] = value
        elif name=="Wind Direction":
            wind_dir = value.split(" ")
            data['wind_dir'] = wind_dir[0]
            data['wind_angle'] = float(wind_dir[1][1:-2])
        elif name=='Wind Speed':
            wind_speed = value.split(" ")
            data['wind_speed'] = float(wind_speed[0])
            data['wind_speed_unit'] = wind_speed[1]
        elif name=='Wind Gust':
            wind_gust = value.split(" ")
            data['wind_gust'] = float(wind_gust[0])
            data['wind_gust_unit'] = wind_gust[1]
        elif name=='Significant Wave Height':
            wave_height = value.split(" ")
            data['wave_height'] = float(wave_height[0])
            data['wave_height_unit'] = wave_height[1]
        elif name=='Dominant Wave Period':
            dominant_wave_period = value.split(" ")
            data['dominant_wave_period'] = float(dominant_wave_period[0])
            data['dominant_wave_period_unit'] = dominant_wave_period[1]            
        elif name=='Average Period':
            average_period = value.split(" ")
            data['average_period'] = float(average_period[0])
            data['average_period_unit'] = average_period[1]            
        elif name=='Mean Wave Direction':
            wave_dir = value.split(" ")
            data['wave_dir'] = wave_dir[0]
            data['wave_angle'] = float(wave_dir[1][1:-2])            
        elif name=='Atmospheric Pressure':
            atmospheric_pressure = value.split(" ")
            data['atmospheric_pressure'] = float(atmospheric_pressure[0])
            data['atmospheric_pressure_unit'] = atmospheric_pressure[1]
        elif name=='Pressure Tendency':
            pressure_tendency = value.split(" ")
            data['pressure_tendency'] = float(pressure_tendency[0])
            data['pressure_tendency_unit'] = pressure_tendency[1]
        elif name=='Air Temperature':
            air_temperature = value.split(" ")[0]
            data['air_temperature'] = float(air_temperature[:-2])
            data['air_temperature_unit'] = air_temperature[-1]
        elif name=='Water Temperature':
            water_temperature = value.split(" ")[0]
            data['water_temperature'] = float(water_temperature[:-2])
            data['water_temperature_unit'] = water_temperature[-1]
        elif name=='Dew Point':
            dew_point = value.split(" ")[0]
            data['dew_point'] = float(dew_point[:-2])
            data['dew_point_unit'] = dew_point[-1]
        elif name=='Visibility':
            visibility = value.split(" ")
            data['visibility'] = float(visibility[0])
            data['visibility_unit'] = visibility[1]
        else:
            data[name] = value
    return data
    

class ObservationsScript(Script):
    
    def get_scheme(self):
        scheme = Scheme("NDBC Observations")
        scheme.description = "Streams observation events from NDBC stations."
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
        if len(stations) == 0:
            raise ValueError("No station id provided (" + stations + ")")

    def stream_events(self, inputs, ew):
        for input_name, input_item in inputs.inputs.iteritems():
            stations = input_item["stations"].split(" ")
            for station in stations:
                url = ENDPOINT.format(id=station)
                xmlstring = requests.get(url).content
                root = ET.fromstring(xmlstring)
                items = root.find('channel').findall('item')
                for item in items:
                    data = get_dict(item)
                    data['id'] = station
                    event = Event()
                    event.stanza = input_name
                    event.sourceType = "ndbc:observations"
                    event.data = json.dumps(data)
                    ew.write_event(event)

if __name__ == "__main__":
    sys.exit(ObservationsScript().run(sys.argv))
