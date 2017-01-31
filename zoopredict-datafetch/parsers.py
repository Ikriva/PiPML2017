# Project in Practical Machine Learning, University of Helsinki, 2017
#
# Parsers for input data formats.
#
# Author: Mika Wahlroos
s

import xml.etree.ElementTree as ElementTree
import dateutil.parser

import datetime
import logging

logging.basicConfig(level=logging.INFO)

namespaces = {
    'wfs': 'http://www.opengis.net/wfs/2.0',
    'gml': 'http://www.opengis.net/gml/3.2',
    'BsWfs': 'http://xml.fmi.fi/schema/wfs/2.0',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
}


class WeatherDaily(object):

    def __init__(self, timestamp, precipitation=None, temp_mean=None, snow_depth=None, temp_min=None, temp_max=None):
        if not isinstance(timestamp, datetime.datetime):
            timestamp = dateutil.parser.parse(timestamp)

        self.timestamp = timestamp
        self.precipitation = precipitation
        self.temp_mean = temp_mean
        self.snow_depth = snow_depth
        self.temp_min = temp_min
        self.temp_max = temp_max

    def as_dict(self):
        return {
            'timestamp': self.timestamp,
            'precipitation': self.precipitation,
            'temp_mean': self.temp_mean,
            'snow_depth': self.snow_depth,
            'temp_min': self.temp_min,
            'temp_max': self.temp_max
        }

    def __repr__(self):
        repr_template = "WeatherObservation(timestamp={ts}, precipitation={prec}, temp_mean={tmean}, " \
             + "snow_depth={snow}, temp_min={tmin}, temp_max={tmax})"
        return repr_template.format(
                ts=repr(self.timestamp), prec=repr(self.precipitation), tmean=repr(self.temp_mean),
                snow=repr(self.snow_depth), tmin=repr(self.temp_min), tmax=repr(self.temp_max)
        )


class FMIWeatherObservationParser(object):

    def __init__(self):
        self.observations = {}

    def parse(self, input_string):
        root = ElementTree.fromstring(input_string)
        for element in root.findall('./wfs:member/BsWfs:BsWfsElement', namespaces=namespaces):
            timestamp_str = element.find('BsWfs:Time', namespaces=namespaces).text
            timestamp = dateutil.parser.parse(timestamp_str)

            observation = self.observations.get(timestamp, None)
            if observation is None:
                observation = WeatherDaily(timestamp)

            if element.find('BsWfs:ParameterName', namespaces=namespaces).text == 'rrday':
                observation.precipitation = float(element.find('BsWfs:ParameterValue', namespaces=namespaces).text)
            elif element.find('BsWfs:ParameterName', namespaces=namespaces).text == 'tday':
                observation.temp_mean = float(element.find('BsWfs:ParameterValue', namespaces=namespaces).text)
            elif element.find('BsWfs:ParameterName', namespaces=namespaces).text == 'tmax':
                observation.temp_max = float(element.find('BsWfs:ParameterValue', namespaces=namespaces).text)
            elif element.find('BsWfs:ParameterName', namespaces=namespaces).text == 'tmin':
                observation.temp_min = float(element.find('BsWfs:ParameterValue', namespaces=namespaces).text)
            elif element.find('BsWfs:ParameterName', namespaces=namespaces).text == 'snow':
                observation.snow_depth = float(element.find('BsWfs:ParameterValue', namespaces=namespaces).text)

            self.observations[timestamp] = observation

    def get_daily_observation(self, timestamp):
        if not isinstance(timestamp, datetime.datetime):
            timestamp = dateutil.parser.parse(timestamp)
        return self.observations[timestamp]

    def get_observations(self):
        return self.observations.values()
