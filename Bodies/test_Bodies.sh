#!/usr/bin/env bash

. ./setenv.sh

echo '============='
echo 'APC'
echo '============='
python test_APCBodies.py "$@"

echo '============='
echo 'Stjarn Himlen'
echo '============='
python test_StjarnHimlen.py "$@"

echo '============'
echo 'Sun Position'
echo '============'
python test_SunPosition.py "$@"

echo '============'
echo 'Moon Position'
echo '============'
python test_MoonPosition.py "$@"
