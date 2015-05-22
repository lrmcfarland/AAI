#!/usr/bin/env bash

. ./setenv.sh

echo '==='
echo 'APC'
echo '==='
python test_APCTransforms.py "$@"

echo '==================='
echo 'Ecliptic Equatorial'
echo '==================='
python test_EclipticEquatorial.py "$@"

echo '=================='
echo 'Equatorial Horizon'
echo '=================='
python test_EquatorialHorizon.py "$@"

echo '============'
echo 'SiderealTime'
echo '============'
python test_SiderealTime.py "$@"

echo '====='
echo 'Utils'
echo '====='
python test_utils.py "$@"
