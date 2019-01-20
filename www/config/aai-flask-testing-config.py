# aai flask pyconfig for testing. This does not have a vaid googemaps key.

import os

DEBUG = True

SECRET_KEY = 'changeme'

# non-flask config is available via config['GOOGLEMAPS_KEY'],
# e.g. {{config['GOOGLEMAPS_KEY']}} in templates

GOOGLEMAPS_KEY = 'changeme'

