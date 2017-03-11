# The Flask web app for ZooPredict
# Provides the web UI for viewing predictions, actual realized values
# and prediction accuracy.

import logging
import logging.config
import os

from flask import Flask, render_template
from flask_babel import Babel
from sklearn.metrics import mean_absolute_error, mean_squared_error, median_absolute_error, accuracy_score

import models
import config


logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object("config")
babel = Babel(app)

# Initialize the SQLAlchemy db with the app to set configuration
models.db.init_app(app)


@app.route("/")
def index():
    with app.app_context():
        results = models.get_zoo_predictions_and_actuals()

    predictions = [{'prediction': row[0], 'actual': row[1]} for row in results]

    predictions_with_observations = list(filter(lambda p: bool(p['actual']), predictions))

    # produce model performance estimates
    regression_preds_tmp = list(map(lambda p: p['prediction'].visitors, predictions_with_observations))
    regression_actuals_tmp = list(map(lambda p: p['actual'].visitors, predictions_with_observations))

    classification_preds_tmp = list(map(lambda p: p['prediction'].visitors_class, predictions_with_observations))
    classification_actuals_tmp = list(map(lambda p: p['actual'].visitors_class, predictions_with_observations))

    mean_squared = mean_squared_error(regression_actuals_tmp, regression_preds_tmp)
    mean_absolute = mean_absolute_error(regression_actuals_tmp, regression_preds_tmp)
    median_absolute = median_absolute_error(regression_actuals_tmp, regression_preds_tmp)
    accuracy = accuracy_score(classification_actuals_tmp, classification_preds_tmp)

    return render_template("index.html",
                           predictions=predictions[:20],
                           mean_squared_error=mean_squared,
                           mean_absolute_error=mean_absolute,
                           median_absolute_error=median_absolute,
                           accuracy=accuracy)


@app.template_filter('visitors_class_to_label')
def visitors_class_to_label(i):
    """
    Returns the visitor class corresponding to the given numeric class.
    :param i:  the numeric class
    :return:   the class label
    """
    return app.config['VISITOR_CLASSES'][i]['label']


if __name__ == "__main__":
    logging.config.dictConfig(config.LOGGING_CONF)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port,debug=config.FLASK_DEBUG)

