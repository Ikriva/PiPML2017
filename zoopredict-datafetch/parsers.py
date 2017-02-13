# Project in Practical Machine Learning, University of Helsinki, 2017
#
# Parsers for input data formats.
#
# Author: Mika Wahlroos

import xml.etree.ElementTree as ElementTree

import models

import datetime
import logging

logging.basicConfig(level=logging.INFO)

namespaces = {
    'wfs': 'http://www.opengis.net/wfs/2.0',
    'gml': 'http://www.opengis.net/gml/3.2',
    'BsWfs': 'http://xml.fmi.fi/schema/wfs/2.0',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
}


class FMIWeatherObservationParser(object):

    def __init__(self):
        self.observations = {}

    def parse(self, input_string):
        root = ElementTree.fromstring(input_string)
        for element in root.findall('./wfs:member/BsWfs:BsWfsElement', namespaces=namespaces):
            timestamp_str = element.find('BsWfs:Time', namespaces=namespaces).text
            date = _parse_fmi_date(timestamp_str)

            observation = self.observations.get(date, None)
            if observation is None:
                observation = models.WeatherObservation(date)

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

            self.observations[date] = observation

    def get_daily_observation(self, date):
        return self.observations[date]

    def get_observations(self):
        return self.observations.values()


def _parse_fmi_date(date_string):
    dt = datetime.datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")
    return datetime.date(year=dt.year, month=dt.month, day=dt.day)
