#!/usr/bin/env python

# Database initialization utility for ZooPredict.
# Populates the database based on the application-wide configuration
# and persistence models.

from __future__ import print_function

import argparse
from flask import Flask
import models


def initdb(app, drop_existing=False):
    print("Flask configuration used for database initialization:")
    print("FLASK_SQLALCHEMY_DATABASE_URI = {u}".format(u=app.config.get('SQLALCHEMY_DATABASE_URI')))
    db = models.db
    db.init_app(app)

    with app.app_context():
        if drop_existing:
            print("Dropping all tables")
            db.drop_all()
        print("Creating tables")
        db.create_all()
        db.session.commit()


def _get_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--drop-existing', dest='drop_existing',
                        action='store_true', default=False,
                        help='drop ALL existing tables before creating new ones')
    return parser


def main():
    app = Flask(__name__)
    app.config.from_object("config")

    argparser = _get_arg_parser()
    args = argparser.parse_args()

    initdb(app, args.drop_existing)

if __name__ == "__main__":
    main()
