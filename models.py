# Persistence models for ZooPredict
# Project in Practical Machine Learning, 2017, University of Helsinki

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class DailyWeather(db.Model):
    """
    Persistence model for daily weather observations and forecasts.
    """

    __abstract__ = True

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

    def as_dict(self):
        return {
            'date': self.date,
            'precipitation': self.precipitation,
            'temp_mean': self.temp_mean,
            'temp_min': self.temp_min,
            'temp_max': self.temp_max
        }


class WeatherObservation(DailyWeather):

    __tablename__ = "weather_observation"


class WeatherForecast(DailyWeather):

    __tablename__ = "weather_forecast"


class ZooStatistic(db.Model):
    """
    Base class for zoo visitor statistic persistence models.
    """
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    visitors = db.Column(db.Integer, nullable=False)
    visitors_class = db.Column(db.Integer, nullable=False)

    def __init__(self, date, visitors, visitors_class):
        self.date = date
        self.visitors = visitors
        self.visitors_class = visitors_class


class ZooStatisticActual(ZooStatistic):
    """
    Persistence model for zoo visitor statistics for a single day.
    """

    __tablename__ = 'zoo_statistic'


class ZooStatisticPrediction(ZooStatistic):
    """
    Persistence model for zoo visitor statistic predictoins for a single day.
    """

    __tablename__ = 'zoo_statistic_prediction'

    classifier_id = db.Column(db.Integer, db.ForeignKey('classifier.id'))
    regression_model_id = db.Column(db.Integer, db.ForeignKey('regression_model.id'))
    classifier = db.relationship('Classifier', foreign_keys=classifier_id)
    regression_model = db.relationship('RegressionModel', foreign_keys=regression_model_id)

    def __init__(self, date, visitors, visitors_class, regression_model=None, classifier=None):
        super(ZooStatisticPrediction, self).__init__(date, visitors, visitors_class)
        self.regression_model = regression_model
        self.classifier = classifier


class PredictionModel(db.Model):
    """
    Base class for persistence models of prediction models.

    The models may be arbitrary objects and are persisted as pickled blobs.
    """
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    model = db.Column(db.PickleType, nullable=False)
    name = db.Column(db.String)

    def __init__(self, model, name=None):
        """
        Initializes a new prediction model persistence instance.
        :param model: the prediction model object
        """
        self.model = model
        self.name = name


class RegressionModel(PredictionModel):

    __tablename__ = "regression_model"


class Classifier(PredictionModel):

    __tablename__ = 'classifier'


def get_zoo_predictions_and_actuals():
    """
    Returns a list of all visitor statistic predictions and actual values.
    If a prediction for a given date exists but an actual value is not available,
    the value for the ZooStatisticActual will be None.
    :return: list of (ZooStatisticPrediction, ZooStatisticActual) tuples
    """

    results = db.session.query(ZooStatisticPrediction)\
                        .outerjoin(ZooStatisticActual,
                                   ZooStatisticPrediction.date == ZooStatisticActual.date)\
                        .order_by(ZooStatisticPrediction.date.desc())\
                        .add_entity(ZooStatisticActual)\
                        .all()
    return results
