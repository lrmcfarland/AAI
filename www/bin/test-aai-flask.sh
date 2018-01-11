#!/usr/bin/env bash
#
# This sets up the shell environment for flask to find the wrapped coords library.
#

. ./bin/setenv.sh

python ./test_aai.py "$@"
