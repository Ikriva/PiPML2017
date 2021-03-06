#!/usr/bin/env python

# A command-line utility that loads weather data and zoo visitor data from CSV
# files and trains scikit-learn classification and regression models based on
# the data.

from __future__ import print_function

import argparse
import collections
import logging
import logging.config
import pickle

import numpy as np
import pandas as pd
from flask import Flask
from sklearn import linear_model
from sklearn.metrics import mean_squared_error, mean_absolute_error, median_absolute_error, make_scorer
from sklearn.model_selection import cross_val_score
from sklearn.svm import SVC

import config
import models

PREDICTORS_WEEKDAYS = ['weekday_' + wd for wd in config.WEEKDAYS]
PREDICTORS_WEATHER = ['temp_max', 'precipitation']
DEFAULT_PREDICTORS = PREDICTORS_WEATHER + PREDICTORS_WEEKDAYS
DEFAULT_CLASSIFICATION_TARGET = 'visitors_class'
DEFAULT_REGRESSION_TARGET = 'visitors'

DEFAULT_VISITORS_TRAINING_DATA_PATH = "data/oldVisitorCounts.csv"
DEFAULT_WEATHER_TRAINING_DATA_PATH = "data/weather_observations_jan-mar_2010-2016.csv"

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

        classes_by_rank = collections.OrderedDict(sorted(visitor_classes_config.items(),
                                                  key=lambda class_dict: class_dict[1]['min']))

        # use numeric indexes as class labels (makes things easier with scikit-learn)
        class_labels = [i for i, c in enumerate(classes_by_rank)]
        class_lower_thresholds = [c['min'] for c in classes_by_rank.values()]

        # Split the data into bins based on the class theresholds.
        # pd.cut seems to want a max value for the last bin too, so add infinity as max.
        class_lower_thresholds.append(float('inf'))

        classification = pd.cut(data['visitors'], class_lower_thresholds,
                                labels=class_labels, include_lowest=True)
        data['visitors_class'] = classification

        # add visitor counts normalized by weekday
        visitors_normalized = data.groupby('weekday')['visitors'].transform(lambda x: x / x.mean())
        data['visitors_normalized'] = visitors_normalized

    def build_classifier(self, predictors=DEFAULT_PREDICTORS, target=DEFAULT_CLASSIFICATION_TARGET, cv=10):
        X = self.data[predictors].as_matrix()
        y = self.data[target].as_matrix()

        classifier = SVC(C=1, kernel='linear')

        # produce accuracy estimate through cross-validation
        if cv:
            scores = cross_val_score(classifier, X, y, cv=cv)
        else:
            scores = None
        classifier.fit(X, y)

        return classifier, scores

    def build_regression_model(self, predictors=DEFAULT_PREDICTORS, target=DEFAULT_REGRESSION_TARGET, cv=10):
        X = self.data[predictors].as_matrix()
        y = self.data[target].as_matrix()

        model = linear_model.LinearRegression()

        # produce accuracy estimate through cross-validation
        if cv:
            scores = {
                'mean_absolute_error':
                    cross_val_score(model, X, y, cv=cv, scoring=make_scorer(mean_absolute_error)),
                'mean_squared_error':
                    cross_val_score(model, X, y, cv=cv, scoring=make_scorer(mean_squared_error)),
                'median_absolute_error':
                    cross_val_score(model, X, y, cv=cv, scoring=make_scorer(median_absolute_error)),
            }
        else:
            scores = None
        model.fit(X, y)
        return model, scores


def weather_to_predictors(daily_weather_data, predictors=DEFAULT_PREDICTORS):
    """
    Takes a list of weather forecasts or observations and returns a feature
    vector ready for passing to a classifier or regression model built by
    ModelBuilder.
    :param daily_weather_data: the daily weather data point
    :return: a prediction model feature vector
    """

    weekdays = [config.WEEKDAYS[w.date.weekday()] for w in daily_weather_data]

    dicts = [w.as_dict() for w in daily_weather_data]

    # construct a data frame and add weekday (not explicitly included in weather data)
    dataframe = pd.DataFrame.from_dict(dicts)
    dataframe['weekday'] = weekdays

    # turn the weekday variable into one-hot predictors
    dataframe = pd.get_dummies(dataframe, columns=['weekday'])

    # fill in columns for the weekday values that didn't appear in the weather observation
    dataframe = dataframe.reindex(columns=predictors).fillna(0, downcast='infer')

    return dataframe[predictors]


def _get_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--store-in-database', dest='store_in_database', action='store_true',
                        help='store the generated models in the database instead of files')
    parser.add_argument('-k', '--keep-existing', dest='keep_existing', action='store_true', default=False,
                        help='keep existing models in the database; by default they are dropped')
    parser.add_argument('-w', '--weather-data-path', dest='weather_data_path',
                        default=DEFAULT_WEATHER_TRAINING_DATA_PATH,
                        help='path the weather data CSV file')
    parser.add_argument('-v', '--visitor-data-path', dest='visitor_data_path',
                        default=DEFAULT_VISITORS_TRAINING_DATA_PATH,
                        help='path to the visitor data CSV file')
    parser.add_argument('-V', '--verbose', dest='verbose', action='store_true',
                        help='more verbose output')
    return parser


def main():
    logging.config.dictConfig(config.LOGGING_CONF)

    app = Flask(__name__)
    app.config.from_object("config")

    argparser = _get_arg_parser()
    args = argparser.parse_args()

    visitor_data = pd.read_csv(args.visitor_data_path)
    weather_data = pd.read_csv(args.weather_data_path)

    builder = ModelBuilder(app, weather_data, visitor_data)
    classifier, classification_scores = builder.build_classifier()
    regr_model, regression_scores = builder.build_regression_model()

    if args.verbose:
        print("Cross-validation accuracies for classification:")
        print(classification_scores)
    print("Mean accuracy (classification): {v}".format(v=np.mean(classification_scores)))
    print("")

    if args.verbose:
        print("Cross-validation MAEs for regression:")
        print(regression_scores)
    print("Mean MSE (regression): {v}".format(v=np.mean(regression_scores['mean_squared_error'])))
    print("Mean MAE (regression): {v}".format(v=np.mean(regression_scores['mean_absolute_error'])))
    print("Mean median absolute error (regression): {v}".format(v=np.mean(regression_scores['median_absolute_error'])))
    print("")

    if args.store_in_database:
        with app.app_context():
            db = models.db
            db.init_app(app)

            if not args.keep_existing:
                existing = models.Classifier.query.all() + models.RegressionModel.query.all()
                for model in existing:
                    db.session.delete(model)

            db.session.add(models.Classifier(classifier, type(classifier).__name__))
            db.session.add(models.RegressionModel(regr_model, type(regr_model).__name__))
            db.session.commit()
    else:
        print("Writing classifier serialization into {p}".format(p=DEFAULT_CLASSIFIER_OUTPUT_PATH))
        with open(DEFAULT_CLASSIFIER_OUTPUT_PATH, 'wb') as f:
            pickle.dump(classifier, f)

        print("Writing regression model serialization into {p}".format(p=DEFAULT_REGRESSION_MODEL_OUTPUT_PATH))
        with open(DEFAULT_REGRESSION_MODEL_OUTPUT_PATH, 'wb') as f:
            pickle.dump(regr_model, f)

if __name__ == "__main__":
    main()
