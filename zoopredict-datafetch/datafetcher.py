# Project in Practical Machine Learning, University of Helsinki, 2017
#
# A module for fetching data from external sources.
#
# Author: Mika Wahlroos

import parsers
import requests
import csv
import logging

logging.basicConfig(level=logging.DEBUG)


def get_daily_fmi_weather_observations(location, start_date, end_date, api_key):
    url_template = "http://data.fmi.fi/fmi-apikey/{api_key}/wfs?request=getFeature&" \
        + "storedquery_id=fmi::observations::weather::daily::simple&place={location}&timestep=1440&" \
        + "starttime={start_date}&endtime={end_date}&"

    url = url_template.format(location=location, start_date=start_date, end_date=end_date, api_key=api_key)
    resp = requests.get(url)
    if resp.status_code != 200:
        raise IOError("Fetching data failed with status code {s}".format(s=resp.status_code))
    if len(resp.text) == 0:
        raise IOError("Got empty response to data request")

    parser = parsers.FMIWeatherObservationParser()
    parser.parse(resp.text)
    return parser.get_observations()


def write_weather_observations(observations, outstream):
    obs_sorted = sorted(observations, key=lambda o: o.date)
    obs_dicts = [o.as_dict() for o in obs_sorted]

    fieldnames = ['date', 'precipitation', 'temp_mean', 'snow_depth', 'temp_min', 'temp_max']
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
