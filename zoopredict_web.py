# The Flask web app for ZooPredict
# Provides the web UI for viewing predictions, actual realized values
# and prediction accuracy.

import logging

from flask import Flask, render_template
from flask_babel import Babel

import models

logging.basicConfig(level=logging.INFO)

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
    app.run()
