# The Flask web app for ZooPredict
# Provides the web UI for viewing predictions, actual realized values
# and prediction accuracy.

import logging
import logging.config

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
    return render_template("index.html")


if __name__ == "__main__":
    logging.config.dictConfig(config.LOGGING_CONF)
    port = int(os.environ.get("PORT", 5000))
    app.run(port=port)

