#!/usr/bin/env bash
#
# This sets up the shell environment for flask to find the wrapped coords library.
#

. ./setenv.sh

python ./astronomy.py "$@"

# EoF
