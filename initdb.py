#!/usr/bin/env python

# Database initialization utility for ZooPredict.
# Populates the database based on the application-wide configuration
# and persistence models.

from __future__ import print_function

from flask import Flask

import models


def initdb(app):
    print("Flask configuration used for database initialization:")
    print("FLASK_SQLALCHEMY_DATABASE_URI = {u}".format(u=app.config.get('SQLALCHEMY_DATABASE_URI')))
    db = models.db
    db.init_app(app)

    with app.app_context():
        print("Creating tables")
        db.create_all()
        db.session.commit()


def main():
    app = Flask(__name__)
    app.config.from_object("config")
    initdb(app)

if __name__ == "__main__":
    main()
