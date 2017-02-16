# Data harvester for external data sources in ZooPredict
# Project in Practical Machine Learning, University of Helsinki, 2017
#
# This module provides a command-line tool for harvesting current
# weather and zoo visitor data from online sources.
# The command-line harvester should be set to automatically run once a day.

import logging
import logging.config
import datetime
import os

from flask import Flask

import models
import config
import datafetcher


logger = logging.getLogger(__name__)


def harvest(app):
    logger.info("Running data harvester")
    db = models.db
    db.init_app(app)

    fmi_api_key = _get_fmi_api_key(app.config['FMI_API_KEY_PATH'])
    location = app.config['FMI_WEATHER_LOCATION']

    # retrieve FMI weather forecast for the next day
    offset = datetime.timedelta(days=1)
    today = datetime.datetime.now().date()

    date = today + offset

    logger.info("Fetching FMI weather forecast data for {d}".format(d=str(date)))
    observations = datafetcher.get_daily_fmi_weather_forecast(location, date, date, fmi_api_key)

    with app.app_context():
        for obs in observations:
            logger.debug("Got observation: {o}".format(o=str(obs)))
            db.session.add(obs)
        db.session.commit()


def _get_fmi_api_key(api_key_path):
    logger.debug("Checking for API key in $FMI_API_KEY")
    api_key = os.environ.get('FMI_API_KEY', None)

    if not api_key:
        # no environment variable found, so try from a file
        logger.debug("Reading API key from {p}".format(p=api_key_path))
        with open(api_key_path, 'r') as f:
            api_key = f.read().strip()

    return api_key


def main():
    """Initializes the database with configuration from the main config file."""
    logging.config.dictConfig(config.LOGGING_CONF)

    app = Flask(__name__)
    app.config.from_object("config")
    harvest(app)

if __name__ == "__main__":
    main()
