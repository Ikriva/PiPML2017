#!/usr/bin/env python

# A command-line utility that loads weather data and zoo visitor data from CSV
# files and learns a scikit-learn model from the data.
# Written for the Project in Practical Machine Learning course, 2017,
# University of Helsinki

import numpy as np
import numpy.lib.recfunctions as recfunctions


def preprocess_weather_data(data):
    pass


def main():
    visitor_data = np.recfromcsv("data/oldVisitorCounts.csv")
    weather_data = np.recfromcsv("data/weather_observations_jan-mar_2010-2016.csv")

    recfunctions.join_by('datetime', weather_data, visitor_data)

    preprocess_weather_data(weather_data.data)


if __name__ == "__main__":
    main()
