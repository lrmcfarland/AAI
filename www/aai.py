#!/usr/bin/env python

"""The Astronomical Algorithms Implemented in C++ and Python

To run:

    ./bin/pylaunch.sh aai.py -c config/aai-flask-testing-config.py

The testing config is a "GET /static/aai.js HTTP/1.1" 304 -
The GOOGLEMAPS_KEY is "changeme"

"""

import argparse
import flask
import logging
import os

import api
import views


# =====================
# ===== utilities =====
# =====================


def factory(a_config_flnm=None):
    """Creates a observations ui flask

    Args:
        conf_flnm (str): configuration filename

    Returns a reference to the AAI app
    """

    config_key = 'AAI_FLASK_CONFIG'

    if a_config_flnm is not None:
        config_flnm = a_config_flnm

    elif os.getenv(config_key) is not None:
        config_flnm = os.environ[config_key]

    else:
        config_flnm = 'config/aai-flask-testing-config.py'
        logging.warning('Using AAI flask test configuration.')


    aai_app = flask.Flask(__name__)

    aai_app.config.from_pyfile(config_flnm)

    aai_app.register_blueprint(views.home_page)
    aai_app.register_blueprint(api.api)

    return aai_app


# ================
# ===== main =====
# ================

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Astronomical Algorithms Implemented')

    parser.add_argument('-c', '--config', type=str, dest='config', default=None,
                        metavar='config',
                        help='The name of the flask config pyfile.')

    args = parser.parse_args()

    # -------------------
    # ----- run app -----
    # -------------------

    app = factory(args.config)

    app.run()
