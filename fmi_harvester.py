# Data harvester for external data sources in ZooPredict
# Project in Practical Machine Learning, University of Helsinki, 2017
#
# This module provides a command-line tool for harvesting current
# weather and zoo visitor data from online sources.
# The command-line harvester should be set to automatically run once a day.

import datetime
import logging
import logging.config
import os

from flask import Flask

import config
import fmi_datafetcher
import models
import train

logger = logging.getLogger(__name__)


class FMIHarvester(object):

    def __init__(self, app):
        self._app = app

    def harvest(self):
        logger.info("Running data harvester")
        db = models.db

        fmi_api_key = _get_fmi_api_key(self._app.config['FMI_API_KEY_PATH'])
        location = self._app.config['FMI_WEATHER_LOCATION']

        # retrieve FMI weather forecast for the next day
        offset = datetime.timedelta(days=1)
        today = datetime.datetime.now().date()

        date = today + offset

        logger.info("Fetching FMI weather forecast data for {d}".format(d=str(date)))
        forecasts = fmi_datafetcher.get_daily_fmi_weather_forecast(location, date, date, fmi_api_key)

        with self._app.app_context():
            classifier = models.Classifier.query.first()
            regression_model = models.RegressionModel.query.first()

            logging.debug("Using classifier: {c}".format(c=classifier.name))
            logging.debug("Using regression model: {r}".format(r=regression_model.name))

            for forecast in forecasts:
                logger.debug("Got forecast: {f}".format(f=str(forecast)))
                db.session.add(forecast)

                predictors = train.weather_to_predictors([forecast])

                predicted_class = classifier.model.predict(predictors)[0].item()
                predicted_visitors = regression_model.model.predict(predictors)[0].item()

                prediction = models.ZooStatisticPrediction(forecast.date,
                                                           predicted_visitors,
                                                           predicted_class,
                                                           regression_model,
                                                           classifier)

                db.session.add(prediction)

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
    logging.config.dictConfig(config.LOGGING_CONF)

    app = Flask(__name__)
    app.config.from_object("config")
    models.db.init_app(app)

    harvester = FMIHarvester(app)
    harvester.harvest()

if __name__ == "__main__":
    main()
