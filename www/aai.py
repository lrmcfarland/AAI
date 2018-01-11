#!/usr/bin/env python

"""The Astronomical Algorithms Implemented in C++ and Python Web UI using Flask

To run: ./bin/pylaunch.sh aai.py

"""

import argparse
import flask
import logging
import logging.handlers


import api
import views



# =====================
# ===== utilities =====
# =====================



def factory(conf_flnm):
    """Creates a observations ui flask

    Blueprints makes this much clearer

    Args:
        conf_flnm (str): configuration filename

    Returns a reference to the flask app
    """

    aai_app = flask.Flask(__name__)
    aai_app.config.from_pyfile(conf_flnm)

    aai_app.register_blueprint(views.home_page)
    aai_app.register_blueprint(api.api)

    return aai_app



# ================
# ===== main =====
# ================

if __name__ == "__main__":

    defaults = {'config': 'conf/aai-flask.cfg',
                'debug': False,
                'host':'0.0.0.0',
                'port': 8080}

    parser = argparse.ArgumentParser(description='Astronomical Algorithms Implemented flask server')

    parser.add_argument('-f', '--config', type=str, dest='config', default=defaults['config'],
                        metavar='config',
                        help='name of config file (default: %(default)s)')

    parser.add_argument('-d', '--debug', action='store_true',
                        dest='debug', default=defaults['debug'],
                        help='flask debug (default: %(default)s)')

    parser.add_argument('--host', type=str, dest='host', default=defaults['host'],
                        metavar='host',
                        help='host IP to serve (default: %(default)s)')

    parser.add_argument('-p', '--port', type=int, dest='port', default=defaults['port'],
                        help='port (default: %(default)s)')

    args = parser.parse_args()

    # -------------------
    # ----- run app -----
    # -------------------

    app = factory(args.config)

    app.run(host=args.host, port=args.port, debug=args.debug)
