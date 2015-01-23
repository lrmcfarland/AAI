#!/usr/bin/env bash

. ./setenv.sh

python test_APCBodies.py "$@"
python test_StjarnHimlen.py "$@"
