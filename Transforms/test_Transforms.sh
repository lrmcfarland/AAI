#!/usr/bin/env bash

. ./setenv.sh

echo '==='
echo 'APC'
echo '==='
PYTHONPATH=../.. python test_APCTransforms.py "$@"

echo '==================='
echo 'Ecliptic Equatorial'
echo '==================='
PYTHONPATH=../.. python test_EclipticEquatorial.py "$@"

echo '=================='
echo 'Equatorial Horizon'
echo '=================='
PYTHONPATH=../.. python test_EquatorialHorizon.py "$@"

echo '============'
echo 'SiderealTime'
echo '============'
PYTHONPATH=../.. python test_SiderealTime.py "$@"

echo '====='
echo 'Utils'
echo '====='
PYTHONPATH=../.. python test_utils.py "$@"
