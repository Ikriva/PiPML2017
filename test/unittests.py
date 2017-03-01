#!/usr/bin/env python

from __future__ import print_function

import unittest
from nose.tools import assert_almost_equals
from nose.tools import assert_is_not_none
from nose.tools import assert_equals
from nose.tools import assert_in
from nose.tools import assert_not_in
from nose.tools import raises
import pandas as pd

import fmi_parser
import initdb
import models
import train
import zoopredict_web


class ZooPredictTest(unittest.TestCase):

    @classmethod
    def setup_class(cls):
        print("Setting up test fixtures")
        app = zoopredict_web.app
        with app.app_context():
            app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite://"
            initdb.initdb(app)

    @classmethod
    def teardown_class(cls):
        print("Tearing down test fixtures")

    def test_fmi_parser(self):
        with open('data/fmi_forecast.xml', 'r') as f:
            xml = f.read()
            parser = fmi_parser.FMIWeatherForecastParser()
            parser.parse(xml, zoopredict_web.app.config['FMI_WEATHER_LOCATION'])
            forecasts = parser.get_forecasts()
            assert_equals(len(forecasts), 1)

            forecast = forecasts[0]
            with zoopredict_web.app.app_context():
                models.db.session.add(forecast)
                models.db.session.commit()

                assert_almost_equals(forecast.temp_max, 2.13)
                assert_almost_equals(forecast.temp_min, 0.65)
                assert_almost_equals(forecast.temp_mean, 1.36375)
                assert_almost_equals(forecast.precipitation, 0.1)

    def test_training(self):
        with zoopredict_web.app.app_context():
            weather_data = pd.read_csv('data/weather_observations.csv')
            visitor_data = pd.read_csv('data/oldVisitorCounts.csv')
            builder = train.ModelBuilder(zoopredict_web.app, weather_data, visitor_data)
            classifier = builder.build_classifier(cv=2)
            regression_model = builder.build_regression_model(cv=2)
            assert_is_not_none(classifier)
            assert_is_not_none(regression_model)

