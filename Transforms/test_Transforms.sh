#!/usr/bin/env bash

. ./setenv.sh

echo '============='
echo 'APC'
echo '============='
python test_APCTransforms.py "$@"

echo '============'
echo 'Sun Position'
echo '============'

echo 'Ecliptic Equatorial'
python test_EclipticEquatorial.py "$@"
echo '- - - - - - '

echo 'Equatorial Horizon'
python test_EquatorialHorizon.py "$@"
echo '- - - - - - '

echo 'GMST'
python test_GMST.py "$@"
echo '- - - - - - '

echo 'Utils'
python test_utils.py "$@"
echo '- - - - - - '
