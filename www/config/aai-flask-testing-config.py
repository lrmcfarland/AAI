# aai flask pyconfig for testing. This does not have a vaid googemaps key.

import os

DEBUG = True

APPLICATION_ROOT = os.getcwd()
SESSION_COOKIE_PATH = os.path.join(os.getcwd(), 'config')

SERVER_NAME = '0.0.0.0:8080'
# TODO https://stackoverflow.com/questions/27254013/why-does-the-session-cookie-work-when-serving-from-a-domain-but-not-when-using-a
SESSION_COOKIE_DOMAIN = SERVER_NAME

SECRET_KEY = 'changeme'

# non-flask available via config['GOOGLEMAPS_KEY'],
# e.g. {{config['GOOGLEMAPS_KEY']}} in templates
GOOGLEMAPS_KEY = 'changeme'

