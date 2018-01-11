#!/usr/bin/env python

"""The Astronomical Algorithms Implemented in C++ and Python Web UI using Flask

To run: ./bin/pylaunch.sh aai.py

with rotating logging: ./pylaunch.sh aai.py -l debug --loghandler rotating --logfilename ./logs/aai-flask.log
"""

import argparse
import flask
import logging
import logging.handlers



home_page = flask.Blueprint('home_blueprint', __name__, template_folder='templates')



@home_page.route("/")
def home():
    """Application's home"""

    return flask.render_template('home.html')


@home_page.route("/accuracy")
def accuracy():
    """Accuracy page"""

    return flask.render_template('accuracy.html')


@home_page.route("/sun_position_chart")
def sun_position_chart():
    """Plot the sun position for the observer's location in space and time"""

    return flask.render_template('sun_position_chart.html')


@home_page.route("/eqhz_transforms")
def eqhz_transforms():
    """Transform equatorial to horizontal coordinates at observer's location in space and time"""

    return flask.render_template('eqhz_transforms.html')


