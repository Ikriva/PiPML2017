#!/usr/bin/env python

# A command-line utility that loads weather data and zoo visitor data from CSV
# files and learns a scikit-learn model from the data.
# Written for the Project in Practical Machine Learning course, 2017,
# University of Helsinki

import logging
import logging.config

import pandas as pd
from sklearn import linear_model
from sklearn.svm import SVC, LinearSVC, SVR, LinearSVR
import numpy as np
from flask import Flask

import config

WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

DEFAULT_PREDICTORS = ['temp_max', 'precipitation'] + ['weekday_' + wd for wd in WEEKDAYS]
DEFAULT_TARGET = 'visitors'

TRAINING_DATA_PATH_VISITORS = "data/oldVisitorCounts.csv"
TRAINING_DATA_PATH_WEATHER = "data/weather_observations_jan-mar_2010-2016.csv"


class ModelBuilder(object):

    def __init__(self, app):
        self._app = app

    def _preprocess_weather_data(self, data):
        # the data contains precipitation values of -1.0 for a lot of days, so
        # set all negative precipitation values to zero
        data.loc[data['precipitation'] < 0.0, 'precipitation'] = 0.0

    def _preprocess_visitor_data(self, data):
        # add visitor count classes to the data frame
        visitor_config = self._app.config['VISITOR_CLASSES']

        visitors_config_kvpairs = sorted(visitor_config.items(), key=lambda kvpair: kvpair[1]['min'])
        class_labels = [i for i, v in enumerate(visitors_config_kvpairs)]
        class_edges = [kvpair[1]['min'] for kvpair in visitors_config_kvpairs]

        # pd.cut seems to want a max value for the last bin too, so add infinity as max
        class_edges.append(float('inf'))

        visitor_classes = pd.cut(data['visitors'], class_edges,
                                 labels=class_labels, include_lowest=True)
        data['visitors_class'] = visitor_classes

        # add visitor counts normalized by weekday
        visitors_normalized = data.groupby('weekday')['visitors'].transform(lambda x: x / x.mean())
        data['visitors_normalized'] = visitors_normalized

    def build_model(self, visitor_data, weather_data, predictors=DEFAULT_PREDICTORS, target=DEFAULT_TARGET):
        self._preprocess_visitor_data(visitor_data)
        self._preprocess_weather_data(weather_data)

        full_data = pd.merge(visitor_data, weather_data, on='datetime')

        # the datetime column is irrelevant as a feature and makes conversion
        # to a numeric array more difficult, so remove it
        del full_data['datetime']

        # convert categorical features to binary numerical features
        full_data = pd.get_dummies(full_data, columns=['weekday'])

        X = full_data[predictors].as_matrix()
        y = full_data[target].as_matrix()

        #model = linear_model.LinearRegression()
        model = SVC()
        model.fit(X, y)
        return model


def main():
    logging.config.dictConfig(config.LOGGING_CONF)

    app = Flask(__name__)
    app.config.from_object("config")

    visitor_data = pd.read_csv(TRAINING_DATA_PATH_VISITORS)
    weather_data = pd.read_csv(TRAINING_DATA_PATH_WEATHER)

    builder = ModelBuilder(app)
    model = builder.build_model(visitor_data, weather_data)


if __name__ == "__main__":
    main()
