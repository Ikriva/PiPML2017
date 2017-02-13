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

    def __init__(self, date):
        self.date = date

    def __repr__(self):
        repr_template = "WeatherObservation(date={date}, precipitation={prec}, temp_mean={tmean}, " \
             + "snow_depth={snow}, temp_min={tmin}, temp_max={tmax})"
        return repr_template.format(
                date=repr(self.date), prec=repr(self.precipitation), tmean=repr(self.temp_mean),
                snow=repr(self.snow_depth), tmin=repr(self.temp_min), tmax=repr(self.temp_max)
        )

    def __str__(self):
        return repr(self)


class ZooStatistic(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    visitors = db.Column(db.Integer, nullable=False)

    def __init__(self, date, visitors):
        self.date = date
        self.visitors = visitors


