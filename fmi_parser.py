# Parsers for input data formats in ZooPredict.
#
# Author: Mika Wahlroos

import xml.etree.ElementTree as ElementTree

import models

import datetime
import logging

logger = logging.getLogger(__name__)

namespaces = {
    'wfs': 'http://www.opengis.net/wfs/2.0',
    'gml': 'http://www.opengis.net/gml/3.2',
    'BsWfs': 'http://xml.fmi.fi/schema/wfs/2.0',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
}

inf = float('inf')


class FMIWeatherObservationParser(object):

    def __init__(self):
        self.observations = {}

    def parse(self, input_string):
        root = ElementTree.fromstring(input_string)
        for element in root.findall('./wfs:member/BsWfs:BsWfsElement', namespaces=namespaces):
            timestamp_str = element.find('BsWfs:Time', namespaces=namespaces).text
            date = parse_fmi_date(timestamp_str)

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

            self.observations[date] = observation

    def get_daily_observation(self, date):
        return self.observations[date]

    def get_observations(self):
        return self.observations.values()


class FMIWeatherForecastParser(object):

    def __init__(self):
        self.forecasts = {}

    def parse(self, input_string, location):
        logger.debug("Parsing weather forecast from XML string")
        location = location.strip()
        root = ElementTree.fromstring(input_string)

        # keep track of all the temperature readings for each day so that a mean can be computed
        hourly_temperatures = {}

        for element in root.findall('./wfs:member/BsWfs:BsWfsElement', namespaces=namespaces):
            datapoint_location = element.find('BsWfs:Location', namespaces=namespaces)\
                                        .find('gml:Point', namespaces=namespaces)\
                                        .find('gml:pos', namespaces=namespaces).text.strip()

            if datapoint_location == location:
                timestamp_str = element.find('BsWfs:Time', namespaces=namespaces).text
                date = parse_fmi_date(timestamp_str)

                daily_forecast = self.forecasts.get(date, None)
                if daily_forecast is None:
                    logger.debug("Found forecast for new data: {d}".format(d=str(date)))
                    daily_forecast = models.WeatherObservation(date, temp_max=-inf, temp_min=inf, precipitation=0.0)
                if date not in hourly_temperatures.keys():
                    hourly_temperatures[date] = []

                if element.find('BsWfs:ParameterName', namespaces=namespaces).text == 'Precipitation1h':
                    point_precipitation = float(element.find('BsWfs:ParameterValue', namespaces=namespaces).text)
                    daily_forecast.precipitation += point_precipitation
                elif element.find('BsWfs:ParameterName', namespaces=namespaces).text == 'Temperature':
                    point_temp = float(element.find('BsWfs:ParameterValue', namespaces=namespaces).text)
                    daily_forecast.temp_max = max(daily_forecast.temp_max, point_temp)
                    daily_forecast.temp_min = min(daily_forecast.temp_min, point_temp)
                    hourly_temperatures[date].append(point_temp)

                self.forecasts[date] = daily_forecast

        logger.debug("Found forecasts for {n} days".format(n=len(self.forecasts)))

        for date, forecast in self.forecasts.items():
            temps = hourly_temperatures[date]
            temp_mean = float(sum(temps)) / max(len(temps), 1)
            forecast.temp_mean = temp_mean

    def get_daily_forecast(self, date):
        return self.forecasts[date]

    def get_forecasts(self):
        return self.forecasts.values()


def parse_fmi_date(date_string):
    """
    Parses a date from the FMI source data XML format.
    :param date_string: the timestamp as a string
    :return: a datetime.date object
    """
    dt = datetime.datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")
    return datetime.date(year=dt.year, month=dt.month, day=dt.day)
