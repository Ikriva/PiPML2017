# Persistence models for ZooPredict
# Project in Practical Machine Learning, 2017, University of Helsinki

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class WeatherObservation(db.Model):
    """
    Persistence model for daily weather observations.
    """

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    temp_max = db.Column(db.Float)
    temp_min = db.Column(db.Float)
    temp_mean = db.Column(db.Float)
    precipitation = db.Column(db.Float)

    def __init__(self, date, temp_max=None, temp_min=None, temp_mean=None, precipitation=None):
        self.date = date
        self.temp_max = temp_max
        self.temp_min = temp_min
        self.temp_mean = temp_mean
        self.precipitation = precipitation

    def __repr__(self):
        repr_template = "WeatherObservation(date={date}, precipitation={prec}, temp_mean={tmean}, " \
             + "temp_min={tmin}, temp_max={tmax})"
        return repr_template.format(
                date=repr(self.date), prec=repr(self.precipitation), tmean=repr(self.temp_mean),
                tmin=repr(self.temp_min), tmax=repr(self.temp_max)
        )

    def __str__(self):
        return repr(self)


class ZooStatistic(db.Model):
    """
    Persistence model for zoo visitor statistics for a single day.
    """

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    visitors = db.Column(db.Integer, nullable=False)
    visitors_class = db.Column(db.Integer, nullable=False)

    def __init__(self, date, visitors, visitors_class):
        self.date = date
        self.visitors = visitors
        self.visitors_class = visitors_class


class PredictionModel(db.Model):
    """
    Persistence model for prediction models.

    The models may be arbitrary objects and are persisted as pickled blobs.
    """

    id = db.Column(db.Integer, primary_key=True)
    model = db.Column(db.PickleType, nullable=False)
    is_classifier = db.Column(db.Boolean, nullable=False)
    name = db.Column(db.String)

    def __init__(self, model, is_classifier, name=None):
        """
        Initializes a new prediction model persistence instance.
        :param model: the prediction model object
        :param is_classifier: should be True for classification models, False for regression
        """
        self.model = model
        self.is_classifier = is_classifier
        self.name = name