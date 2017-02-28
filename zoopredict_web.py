# The Flask web app for ZooPredict
# Provides the web UI for viewing predictions, actual realized values
# and prediction accuracy.

import logging
import logging.config
import os

from flask import Flask, render_template
from flask_babel import Babel

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

    daily_predictions = [{'prediction': row[0], 'actual': row[1]} for row in results]

    return render_template("index.html", predictions=daily_predictions[:5])


if __name__ == "__main__":
    logging.config.dictConfig(config.LOGGING_CONF)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port,debug=config.FLASK_DEBUG)

