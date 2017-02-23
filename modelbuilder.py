#!/usr/bin/env python

# A command-line utility that loads weather data and zoo visitor data from CSV
# files and learns a scikit-learn model from the data.
# Written for the Project in Practical Machine Learning course, 2017,
# University of Helsinki

from __future__ import print_function

import collections
import logging
import logging.config
import pickle

import pandas as pd
from sklearn.model_selection import cross_val_score
from sklearn import linear_model
from sklearn.svm import SVC, LinearSVC, SVR, LinearSVR
import numpy as np
from flask import Flask

import config

WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

DEFAULT_PREDICTORS = ['temp_max', 'precipitation'] + ['weekday_' + wd for wd in WEEKDAYS]
DEFAULT_CLASSIFICATION_TARGET = 'visitors_class'
DEFAULT_REGRESSION_TARGET = 'visitors'

TRAINING_DATA_PATH_VISITORS = "data/oldVisitorCounts.csv"
TRAINING_DATA_PATH_WEATHER = "data/weather_observations_jan-mar_2010-2016.csv"

DEFAULT_CLASSIFIER_OUTPUT_PATH = "classifier.dump"
DEFAULT_REGRESSION_MODEL_OUTPUT_PATH = "regression_model.dump"

logger = logging.getLogger(__name__)


class ModelBuilder(object):

    def __init__(self, app, weather_data, visitor_data):
        self._app = app

        self._preprocess_weather_data(weather_data)
        self._preprocess_visitor_data(visitor_data)
        full_data = pd.merge(visitor_data, weather_data, on='datetime')

        # the datetime column is irrelevant as a feature and makes conversion
        # to a numeric array more difficult, so remove it
        del full_data['datetime']

        # convert categorical features to binary numerical features
        self.data = pd.get_dummies(full_data, columns=['weekday'])

    def _preprocess_weather_data(self, data):
        # the data contains precipitation values of -1.0 for a lot of days, so
        # set all negative precipitation values to zero
        data.loc[data['precipitation'] < 0.0, 'precipitation'] = 0.0

    def _preprocess_visitor_data(self, data):
        # add visitor count classes to the data frame
        visitor_classes_config = self._app.config['VISITOR_CLASSES']

        classes = collections.OrderedDict(sorted(visitor_classes_config.items(),
                                          key=lambda class_dict: class_dict[1]['min']))

        logging.debug("Classes config after sorting: {c}".format(c=classes))

        # use numeric indexes as class labels (easier with scikit-learn)
        class_labels = [i for i, c in enumerate(classes)]
        class_lower_thresholds = [c['min'] for c in classes.values()]

        # pd.cut seems to want a max value for the last bin too, so add infinity as max
        class_lower_thresholds.append(float('inf'))

        visitor_classes = pd.cut(data['visitors'], class_lower_thresholds,
                                 labels=class_labels, include_lowest=True)
        data['visitors_class'] = visitor_classes

        # add visitor counts normalized by weekday
        visitors_normalized = data.groupby('weekday')['visitors'].transform(lambda x: x / x.mean())
        data['visitors_normalized'] = visitors_normalized

    def build_classifier(self, predictors=DEFAULT_PREDICTORS, target=DEFAULT_CLASSIFICATION_TARGET):
        X = self.data[predictors].as_matrix()
        y = self.data[target].as_matrix()

        classifier = SVC()

        scores = cross_val_score(classifier, X, y, cv=10)

        classifier.fit(X, y)
        return classifier, scores

    def build_regression_model(self, predictors=DEFAULT_PREDICTORS, target=DEFAULT_REGRESSION_TARGET):
        X = self.data[predictors].as_matrix()
        y = self.data[target].as_matrix()

        model = linear_model.LinearRegression()
        model.fit(X, y)
        return model


def main():
    logging.config.dictConfig(config.LOGGING_CONF)

    app = Flask(__name__)
    app.config.from_object("config")

    visitor_data = pd.read_csv(TRAINING_DATA_PATH_VISITORS)
    weather_data = pd.read_csv(TRAINING_DATA_PATH_WEATHER)

    builder = ModelBuilder(app, weather_data, visitor_data)
    classifier, classification_scores = builder.build_classifier()
    print("Cross-validation accuracies for classification:")
    print(classification_scores)
    print("Mean accuracy: {v}".format(v=np.mean(classification_scores)))

    with open(DEFAULT_CLASSIFIER_OUTPUT_PATH, 'w') as f:
        pickle.dump(classifier, f)

    regr_model = builder.build_regression_model()

    with open(DEFAULT_REGRESSION_MODEL_OUTPUT_PATH, 'w') as f:
        pickle.dump(regr_model, f)

if __name__ == "__main__":
    main()
