#!/usr/bin/env bash
#
# This sets up the shell environment for gunicorn to find the wrapped coords library.
#

. ./setenv.sh

gunicorn astronomy:app "$@"

# -b 0.0.0.0:8080 -w 4 astronomy:app
#
# TODO host, port, workers from cli "$@". more options?
# TODO nginx as TLS reverse proxy and no direct access to this. -b 127.0.0.1:4000?
