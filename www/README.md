# AAI server

This directory contains the source code to create the
AAI web server.
It is built on the [Flask](http://flask.pocoo.org)
microframework.

# Prerequisites


I developed this mostly on OSX using [brew](https://brew.sh/) to install everything else.

It uses my [Coordinates](https://github.com/lrmcfarland/Coordinates) library (developed mostly on Linux).

This version uses the starbug.coords PyPI package.


## Create a virtual python environment

While not strictly necessary, it is helpful to create a virtual python
environment to run in. I started with virtualenv, upgraded to pyenv
and expect to use -m env with python3 in the future.


### Setup [pyenv](https://github.com/pyenv/pyenv)

On OS X with brew

```
    brew install pyenv-virtualenv
```

### env

Run these commands in your shell to support activating a virtualenv,
but move them to ~/.bashrc to make permanent.

```
    eval "$(pyenv init -)"
    eval "$(pyenv virtualenv-init -)"
```

#### To create python virtualenv

```
    pyenv virtualenv 3.7.0 test-coords
```

#### Activate an env

```
    pyenv activate test-coords
```

#### pip install requirements

Add the required libraries from AAI/requirements.txt

```
$ pip install -r requirements.txt
Collecting requirements.txt

$ pip list
Package        Version
-------------- -------
Click          7.0
Flask          1.0.2
gunicorn       19.9.0
itsdangerous   1.1.0
Jinja2         2.10
MarkupSafe     1.1.1
pip            19.0.3
setuptools     39.0.1
starbug.coords 1.0.0
Werkzeug       0.14.1

```



## AAI config


An example configuration file for the flask server is located in
[config/aai-flask-testing-config.py](https://github.com/lrmcfarland/AAI/blob/master/www/config/aai-flask-testing-config.py).
It takes the usual [flask configuration
parameters](http://flask.pocoo.org/docs/1.0/config/) and a
GOOGLEMAPS_KEY.
The checked in version does not have a vaild GOOGLEMAPS_KEY so the map
won't display until it does, but the web page should come up
and the API will function.
A real deployment should include a real GOOGLEMAPS_KEY and
change the flask SECRET_KEY.

# Running the AAI server

To run the server in the AAI/www directory from the command line at
the AAI root

```
$ PYTHONPATH=../.. python aai.py -c config/aai-flask-testing-config.py
 * Serving Flask app "aai" (lazy loading)
 * Environment: production
   WARNING: Do not use the development server in a production environment.
   Use a production WSGI server instead.
 * Debug mode: on
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 229-268-553

```

The web page should now be available on the local host at the
place indicated above.


```
$ curl http://127.0.0.1:5000/api/v1/dms2dec?dms="1:30"
{
  "dec": "1.5",
  "errors": []
}
```



# Troubleshooting

## Debugger

Use the python debugger

```

$ PYTHONPATH=../.. python -m pdb aai.py -c config/aai-flask-testing-config.py
> /Users/lrm/src/starbug/AAI/www/aai.py(10)<module>()
-> """
(Pdb) b aai.factory
Breakpoint 1 at /Users/lrm/src/starbug/AAI/www/aai.py:26
(Pdb) c
> /Users/lrm/src/starbug/AAI/www/aai.py(35)factory()
-> config_key = 'AAI_FLASK_CONFIG'

(Pdb) l
 30		conf_flnm (str): configuration filename
 31
 32	    Returns a reference to the AAI app
 33	    """
 34
 35  ->	    config_key = 'AAI_FLASK_CONFIG'
 36
 37	    if a_config_flnm is not None:
 38		config_flnm = a_config_flnm
 39
 40	    elif os.getenv(config_key) is not None:


```

## Flask DEBUG

Set the flask debug flag to True in the flask config file:

```
DEBUG = True

```


## GOOGLEMAP_KEY

If the GOOGLEMAP_KEY is invalid, this line shows up in the log file:

```
127.0.0.1 - - [18/Jan/2019 14:35:31] "GET /static/aai.js HTTP/1.1" 304 -

```

Providing a valid map key should fix it.
