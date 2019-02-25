#!/usr/bin/env bash

. ./setenv.sh

echo '============='
echo 'APC'
echo '============='
PYTHONPATH=../.. python test_APCBodies.py "$@"

echo '============='
echo 'Stjarn Himlen'
echo '============='
PYTHONPATH=../.. python test_StjarnHimlen.py "$@"

echo '============'
echo 'Sun Position'
echo '============'
PYTHONPATH=../.. python test_SunPosition.py "$@"
