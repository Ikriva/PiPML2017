# Persistence models for ZooPredict
# Project in Practical Machine Learning, 2017, University of Helsinki

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class WeatherObservation(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    temp_max = db.Column(db.Float)
    temp_min = db.Column(db.Float)
    temp_mean = db.Column(db.Float)
    precipitation = db.Column(db.Float)
    snow_depth = db.Column(db.Float)

    def __init__(self, temp_max, date, temp_min, temp_mean, precipitation, snow_depth):
        self.temp_max = temp_max
        self.date = date
        self.temp_min = temp_min
        self.temp_mean = temp_mean
        self.precipitation = precipitation
        self.snow_depth = snow_depth


class ZooStatistic(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    visitors = db.Column(db.Integer, nullable=False)

    def __init__(self, date, visitors):
        self.date = date
        self.visitors = visitors


