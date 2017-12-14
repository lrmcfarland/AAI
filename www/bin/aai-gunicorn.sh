#!/usr/bin/env bash
#
# This sets up the shell environment for gunicorn to find the wrapped coords library.
#

. ./bin/setenv.sh

gunicorn aai:app "$@"
