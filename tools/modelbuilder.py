#!/usr/bin/env python

# A command-line utility that loads weather data and zoo visitor data from CSV
# files and learns a scikit-learn model from the data.
# Written for the Project in Practical Machine Learning course, 2017,
# University of Helsinki

import pandas as pd
import numpy as np

VISITOR_CLASS_LABELS = ["low", "medium", "high"]
WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def preprocess_weather_data(data):
    pass


def preprocess_visitor_data(data):
    # add visitor count classes to the data frame
    visitor_classes = pd.qcut(data['visitors'], len(VISITOR_CLASS_LABELS), labels=VISITOR_CLASS_LABELS)
    data['visitors_class'] = visitor_classes

    # add visitor counts normalized by weekday
    visitors_normalized = data.groupby('weekday')['visitors'].transform(lambda x: x / x.mean())
    data['visitors_normalized'] = visitors_normalized


def main():
    visitor_data = pd.read_csv("data/oldVisitorCounts.csv")
    weather_data = pd.read_csv("data/weather_observations_jan-mar_2010-2016.csv")

    preprocess_weather_data(weather_data.data)

    full_data = pd.merge(visitor_data, weather_data, on='datetime')


if __name__ == "__main__":
    main()
