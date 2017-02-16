# Configuration for ZooPredict
# Project in Practical Machine Learning, University of Helsinki, 2017
#
# The same configuration is used by both the data harvester and the web UI.

#SQLALCHEMY_DATABASE_URI = "sqlite:///zoopredict.db"
SQLALCHEMY_DATABASE_URI = "sqlite://"

DEBUG = True
FLASK_DEBUG = False

#FMI_WEATHER_LOCATION = "kaisaniemi"
#FMI_WEATHER_LOCATION = "60.17523 24.94459" # Kaisaniemi
FMI_WEATHER_LOCATION = "60.16952 24.93545"  # Helsinki
FMI_API_KEY_PATH = "fmi_api_key.txt"

# based on the configuration example at
# https://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python/
LOGGING_CONF = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': True
        }
    }
}
