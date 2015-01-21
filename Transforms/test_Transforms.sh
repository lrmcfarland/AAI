#!/usr/bin/env bash

. ./setenv.sh

python test_APCTransforms.py "$@"
python test_EclipticEquatorial.py "$@"
python test_EquatorialHorizon.py "$@"
python test_GMST.py "$@"
python test_StjarnHimlen.py "$@"
python test_utils.py "$@"
