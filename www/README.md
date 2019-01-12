# SunPosition Web UI using Flask

This is the initial Web UI for my astronomy tool kit. I use
[Flask](http://flask.pocoo.org) to create the templates for the sun
position calculation.

# From the command line

## Setup [pyenv](https://github.com/pyenv/pyenv)

### On OS X with brew

```
    brew install pyenv-virtualenv

```

### env

Run these commands in your shell but move to .bashrc to make permanent.

```
    eval "$(pyenv init -)"
    eval "$(pyenv virtualenv-init -)"

```

Create python 2.7 or 3.7 envs

```

    pyenv install 2.7.15
    pyenv install 3.7.0

    pyenv virtualenv 2.7.15 sb-py2
    pyenv virtualenv 3.7.0 sb-py3


    $ pyenv virtualenvs
    2.7.15/envs/sb-py2 (created from /Users/lrm/.pyenv/versions/2.7.15)
    3.7.0/envs/sb-py3 (created from /Users/lrm/.pyenv/versions/3.7.0)
    sb-py2 (created from /Users/lrm/.pyenv/versions/2.7.15)
    sb-py3 (created from /Users/lrm/.pyenv/versions/3.7.0)


    pyenv activate sb-py2


```

Add the required libraries from AAI/requirements.txt

```


(sb-py2) lrmz-iMac:AAI lrm$ pip install -r requirements.txt
Collecting requirements.txt


```



## Superseded: setup virtualenv

Here pyenv is local not the application described above.

one time setup

```
lrm@lrmz-iMac AAI (master)]$ pwd
/Users/lrm/src/starbug/AAI

[lrm@lrmz-iMac AAI (master)]$ mkdir pyenv

[lrm@lrmz-iMac AAI (master)]$ virtualenv pyenv
New python executable in /Users/lrm/src/starbug/AAI/pyenv/bin/python
Installing setuptools, pip, wheel...done.

[lrm@lrmz-iMac AAI (master)]$ source pyenv/bin/activate
(pyenv) [lrm@lrmz-iMac AAI (master)]$ pip list
DEPRECATION: The default format will switch to columns in the future. You can use --format=(legacy|columns) (or define a format=(legacy|columns) in your pip.conf under the [list] section) to disable this warning.
pip (9.0.1)
setuptools (38.2.4)
wheel (0.30.0)


(pyenv) [lrm@lrmz-iMac AAI (master)]$ pip list
DEPRECATION: The default format will switch to columns in the future. You can use --format=(legacy|columns) (or define a format=(legacy|columns) in your pip.conf under the [list] section) to disable this warning.
pip (9.0.1)
setuptools (38.2.4)
wheel (0.30.0)


(pyenv) [lrm@lrmz-iMac AAI (master)]$ pip install flask
Collecting flask
  Using cached Flask-0.12.2-py2.py3-none-any.whl
Collecting Jinja2>=2.4 (from flask)
  Using cached Jinja2-2.10-py2.py3-none-any.whl
Collecting Werkzeug>=0.7 (from flask)
  Using cached Werkzeug-0.13-py2.py3-none-any.whl
Collecting click>=2.0 (from flask)
  Using cached click-6.7-py2.py3-none-any.whl
Collecting itsdangerous>=0.21 (from flask)
  Using cached itsdangerous-0.24.tar.gz
Collecting MarkupSafe>=0.23 (from Jinja2>=2.4->flask)
  Using cached MarkupSafe-1.0.tar.gz
Building wheels for collected packages: itsdangerous, MarkupSafe
  Running setup.py bdist_wheel for itsdangerous ... done
  Stored in directory: /Users/lrm/Library/Caches/pip/wheels/fc/a8/66/24d655233c757e178d45dea2de22a04c6d92766abfb741129a
  Running setup.py bdist_wheel for MarkupSafe ... done
  Stored in directory: /Users/lrm/Library/Caches/pip/wheels/88/a7/30/e39a54a87bcbe25308fa3ca64e8ddc75d9b3e5afa21ee32d57
Successfully built itsdangerous MarkupSafe
Installing collected packages: MarkupSafe, Jinja2, Werkzeug, click, itsdangerous, flask
Successfully installed Jinja2-2.10 MarkupSafe-1.0 Werkzeug-0.13 click-6.7 flask-0.12.2 itsdangerous-0.24


(pyenv) [lrm@lrmz-iMac AAI (master)]$ pip list --format=columns
Package      Version
------------ -------
click        6.7
Flask        0.12.2
itsdangerous 0.24
Jinja2       2.10
MarkupSafe   1.0
pip          9.0.1
setuptools   38.2.4
Werkzeug     0.13
wheel        0.30.0


```

## config

use git diff to keep track


### flask secret

change secret in conf/aai-flask.cfg

```
$ more www/conf/aai-flask.cfg
# base line aai flask config

SECRET_KEY = 'changeme'

```


## Run pylanuch.sh

```

(pyenv) [lrm@lrmz-iMac www (master)]$ ./bin/pylaunch.sh aai.py -h
# COORDS_ROOT not set. Using ..
# coords.so: ../Coordinates/Python/Boost/build/lib.macosx-10.12-intel-2.7/coords.so
# DYLD_LIBRARY_PATH :../Coordinates/libCoords
# PYTHONPATH :../Coordinates/Python/Boost/build/lib.macosx-10.12-intel-2.7:..

usage: aai.py [-h] [-d] [--host host] [--logfilename logfilename]
	      [--loghandler HANDLER] [-l LEVEL] [-p PORT]

Astronomical Algorithms Implemented flask server

optional arguments:
  -h, --help            show this help message and exit
  -d, --debug           flask debug (default: False)
  --host host           host IP to serve (default: 0.0.0.0)
  --logfilename logfilename
			name of log file (default:
			/opt/starbug.com/logs/flask)
  --loghandler HANDLER  logging handler choice: rotating, stream (default:
			stream)
  -l LEVEL, --loglevel LEVEL
			logging level choice: debug, info, warn, error
			(default: warn)
  -p PORT, --port PORT  port (default: 8080)

```


# Docker install

See ../Dockerfile.flask

# Manual Apache Install

see Readme_apache.md

