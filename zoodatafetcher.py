# Zoo Data harvester and extractor for external data sources in ZooPredict
# Project in Practical Machine Learning, University of Helsinki, 2017
#
# This is run periodically once a day from command line.

import openpyxl.reader.excel
import urllib.request
import os
import datetime
import models
import config
from flask import Flask
import logging
import logging.config
from datetime import date


logger = logging.getLogger(__name__)


def zoodatafetcher(app, history=False):
    logger.info("Running zoo data harvester")
    # Names that match the sheet names in the source Excel workbook for month collection
    month_dict = ["Tammikuu", "Helmikuu", "Maaliskuu", "Huhtikuu", "Toukokuu"]

    datafile = 'Ktkuluva.xlsx'
    if os._exists(datafile):
        os.remove(datafile)
    url = "http://datastore.hri.fi/Helsinki/zoo/Ktkuluva.xlsx"
    urllib.request.urlretrieve(url, 'Ktkuluva.xlsx')

    workbook = openpyxl.reader.excel.load_workbook(datafile, read_only=True, data_only=True)

    if history is False:
        # The default option
        # Assumed the script will always check yesterday's statistics as current day statistics are unavailable
        date = datetime.date.today() - datetime.timedelta(days=1)
        sheet = workbook[month_dict[date.month - 1]]
        _save_to_db(app, _read_daylist_from_month_statistic(sheet, [date]))

    else:
        # get history data too. To be written later
        pass


def _read_daylist_from_month_statistic(worksheet, dates):
    values = list(worksheet.iter_rows())[5:36]
    result = []
    for day in dates:
        value = values[day.day-1][3].value
        # Assumption is that values are continuous until the day count is empty for future days
        if value is None:
            break
        result.append(models.ZooStatistic(day, value, _visitor_class_resolver(value)))
    return result


def _save_to_db(app, list):
    models.db.init_app(app)
    with app.app_context():
        for object in list:
            models.db.session.add(object)
        models.db.session.commit()


def _visitor_class_resolver(count):
    visitor_class = 99
    for item,value in config.VISITOR_CLASSES.items():
        if count > value['min']:
            visitor_class = item
    return visitor_class


def main():
    """Initializes the database with configuration from the main config file."""
    logging.config.dictConfig(config.LOGGING_CONF)

    app = Flask(__name__)
    app.config.from_object("config")
    zoodatafetcher(app)

if __name__ == "__main__":
    main()


