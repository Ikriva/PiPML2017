# Project in Practical Machine Learning, University of Helsinki, 2017
#
# A module for fetching data from external sources.
#
# Author: Mika Wahlroos

import fmi_parser
import requests
import csv
import datetime
import logging


logger = logging.getLogger(__name__)


def get_daily_fmi_weather_forecast(location, start_date, end_date, api_key):
    """
    Retrieves daily weather forecasts from FMI.
    The result is a list of models.WeatherObservation objects.
    The daily minimum, maximum and mean temperatures as well as daily total
    precipitation expressed by a WeatherObservation object are computed from
    the hourly forecast values returned from the FMI service, so e.g.
    precipitation in the result is a computed total from the hourlies.

    :param location: the location for which to obtain the forecast, as coordinates
    :param start_date: the first date to include in the forecast
    :param end_date: the last date to include in the forecast
    :param api_key: the FMI API key
    :return: a list of models.WeatherObservation objects, one observation per day
    """
    url_template = "http://data.fmi.fi/fmi-apikey/{api_key}/wfs?request=getFeature&" \
        + "storedquery_id=fmi::forecast::hirlam::surface::cities::simple&timestep=60&" \
        + "starttime={start_time}&endtime={end_time}&"

    # get the hourly forecasts in the range from start_date at 00:00 to end_date at 23:59
    start_time = datetime.datetime.combine(start_date, datetime.time(hour=0))
    end_time = datetime.datetime.combine(end_date, datetime.time(hour=23, minute=59))

    url = url_template.format(location=location,
                              start_time=start_time.isoformat(),
                              end_time=end_time.isoformat(),
                              api_key=api_key)
    resp = requests.get(url)
    if resp.status_code != 200:
        raise IOError("Fetching data failed with status code {s}".format(s=resp.status_code))
    if len(resp.text) == 0:
        raise IOError("Got empty response to data request")

    parser = fmi_parser.FMIWeatherForecastParser()
    parser.parse(resp.text, location)
    return parser.get_forecasts()


def get_daily_fmi_weather_observations(location, start_date, end_date, api_key):
    """
    Retrieves daily weather observations from FMI.
    The result is a list of models.WeatherObservation objects.
    :param location: the name of the geographical location from which to get observations
    :param start_date: the first date to include in the observations
    :param end_date: the last date to include in the observations
    :param api_key: the FMI API key
    :return: a list of models.WeatherObservation objects, one observation per day
    """
    url_template = "http://data.fmi.fi/fmi-apikey/{api_key}/wfs?request=getFeature&" \
        + "storedquery_id=fmi::observations::weather::daily::simple&place={location}&timestep=1440&" \
        + "starttime={start_date}&endtime={end_date}&"

    url = url_template.format(location=location, start_date=start_date, end_date=end_date, api_key=api_key)
    resp = requests.get(url)
    if resp.status_code != 200:
        raise IOError("Fetching data failed with status code {s}".format(s=resp.status_code))
    if len(resp.text) == 0:
        raise IOError("Got empty response to data request")

    parser = fmi_parser.FMIWeatherObservationParser()
    parser.parse(resp.text)
    return parser.get_observations()


def write_weather_observations(observations, outstream):
    obs_sorted = sorted(observations, key=lambda o: o.date)
    obs_dicts = [_weather_observation_to_dict(o) for o in obs_sorted]

    fieldnames = ['date', 'precipitation', 'temp_mean', 'temp_min', 'temp_max']
    writer = csv.DictWriter(outstream, fieldnames=fieldnames)
    writer.writeheader()
    for d in obs_dicts:
        writer.writerow(d)


def get_weather_observation_history(apikey, output_path):
    """Utility method for getting the needed weather observation history"""

    location = 'kaisaniemi'
    all_obs = []

    for year in ['2010', '2011', '2012', '2013', '2014', '2015', '2016']:
        #obs = get_daily_fmi_weather_observations(location, year+'-01-01', year+'-12-31', apikey)
        obs = get_daily_fmi_weather_observations(location, year + '-01-01', year + '-03-31', apikey)
        all_obs.extend(obs)

    with open(output_path, "w") as f:
        write_weather_observations(all_obs, f)


def _weather_observation_to_dict(observation):
    return {
        'date': observation.date,
        'precipitation': observation.precipitation,
        'temp_mean': observation.temp_mean,
        'temp_min': observation.temp_min,
        'temp_max': observation.temp_max
    }
