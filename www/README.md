# AAI server

This directory contains the source code to create the
AAI web server.
It is built on the [Flask](http://flask.pocoo.org)
microframework.

# Prerequisites


I developed this mostly on OSX using [brew](https://brew.sh/) to install everything else.

It uses my [Coordinates](https://github.com/lrmcfarland/Coordinates) library (developed mostly on Linux).


## Build Coordinates

The Coordinates library is written in C++.
This library needs to be build and on the PYTHONPATH for this to run.
I have built it with g++ (on Linux) and clang++ (on OSX with xcode-select installed).
After it is built, the
[setenv.sh](https://github.com/lrmcfarland/AAI/blob/master/www/bin/setenv.sh)
bash scripts add the Coordinates library to the PYTHONPATH for the
"launching" scritps in
[www/bin](https://github.com/lrmcfarland/AAI/tree/master/www/bin):
- [pylanuch.sh](https://github.com/lrmcfarland/AAI/blob/master/www/bin/pylaunch.sh),
- [test-aai-flask.sh](https://github.com/lrmcfarland/AAI/blob/master/www/bin/test-aai-flask.sh),
- [aai-flask.sh](https://github.com/lrmcfarland/AAI/blob/master/www/bin/aai-flask.sh),
- [aai-gunicorn.sh](https://github.com/lrmcfarland/AAI/blob/master/www/bin/aai-gunicorn.sh)

It is included in the AAI repo as a git submodule.

### Checkout the Coordinates submodule

In the AAI root directory

```
git submodule update --init --recursive
```

### Build the Coordinates library

The Coordinates
[build.sh](https://github.com/lrmcfarland/Coordinates/blob/master/build.sh)
script will build and test the coordinates library and its python wrappers.

The script takes optional arguments clean and test.


```
$ ./build.sh test
======================================================================
./libCoords
clang++ -g -W -Wall -fPIC -I. -std=c++11   -c -o angle.o angle.cpp
clang++ -g -W -Wall -fPIC -I. -std=c++11   -c -o Cartesian.o Cartesian.cpp
clang++ -g -W -Wall -fPIC -I. -std=c++11   -c -o datetime.o datetime.cpp
clang++ -g -W -Wall -fPIC -I. -std=c++11   -c -o spherical.o spherical.cpp
clang++ -g -W -Wall -fPIC -I. -std=c++11   -c -o utils.o utils.cpp
rm -f libCoords.a
ar cq libCoords.a angle.o Cartesian.o datetime.o spherical.o utils.o
ranlib libCoords.a
rm -f libCoords.1.0.0.dylib libCoords.dylib libCoords.1.dylib libCoords.1.0.dylib
clang++ -headerpad_max_install_names -single_module -dynamiclib -compatibility_version 1.0 -current_version 1.0.0 -install_name /Users/rmcfarland/fubar/AAI/Coordinates/libCoords/libCoords.1.dylib -o libCoords.1.0.0.dylib angle.o Cartesian.o datetime.o spherical.o utils.o
ln -s libCoords.1.0.0.dylib libCoords.dylib
ln -s libCoords.1.0.0.dylib libCoords.1.dylib
ln -s libCoords.1.0.0.dylib libCoords.1.0.dylib
======================================================================
./Python/Manual
env ARCHFLAGS="-arch x86_64" python setup.py build
running build
running build_ext
building 'coords' extension

...


```


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
    pyenv install 2.7.15
    pyenv virtualenv 2.7.15 aai-py2
```

for python3

```
    pyenv install 3.7.0
    pyenv virtualenv 3.7.0 aai-py3
```

#### Activate an env

```
    pyenv activate aai-py2
```

#### pip install requirements

Add the required libraries from AAI/requirements.txt

```
$ pip install -r requirements.txt
Collecting requirements.txt

$ pip list
Package      Version
------------ -------
Click        7.0
Flask        1.0.2
gunicorn     19.9.0
itsdangerous 1.1.0
Jinja2       2.10
MarkupSafe   1.1.0
pip          18.1
setuptools   40.6.3
Werkzeug     0.14.1
wheel        0.32.3
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
the AAI root use pylaunch.sh.

```
$ ./bin/pylaunch.sh aai.py -h
# COORDS_ROOT not set. Using ..
# coords.so: ../Coordinates/Python/Boost/build/lib.macosx-10.13-x86_64-2.7/coords.so
# DYLD_LIBRARY_PATH :../Coordinates/libCoords
# PYTHONPATH :../Coordinates/Python/Boost/build/lib.macosx-10.13-x86_64-2.7:..

usage: aai.py [-h] [-c config]

Astronomical Algorithms Implemented

optional arguments:
  -h, --help            show this help message and exit
  -c config, --config config
			The name of the flask config pyfile.

```
The config file is set from the command line arguments (or the
AAI_FLASK_CONFIG environment variable), defaulting
to the aai-flask-testing-config.py.


```
$ ./bin/pylaunch.sh aai.py -c config/aai-flask-testing-config.py
# COORDS_ROOT not set. Using ..
# coords.so: ../Coordinates/Python/Boost/build/lib.macosx-10.13-x86_64-2.7/coords.so
# DYLD_LIBRARY_PATH :../Coordinates/libCoords
# PYTHONPATH :../Coordinates/Python/Boost/build/lib.macosx-10.13-x86_64-2.7:..

 * Serving Flask app "aai" (lazy loading)
 * Environment: production
   WARNING: Do not use the development server in a production environment.
   Use a production WSGI server instead.
 * Debug mode: on
 * Running on http://0.0.0.0:8080/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 247-038-127


```

The web page should now be available on the local host at the
place indicated above.


```
$ curl http://0.0.0.0:8080/api/v1/dms2dec?dms="1:30"
{
  "dec": "1.5",
  "errors": []
}

```



# Troubleshooting

## Debugger

Use the python debugger

```

$ ./bin/pylaunch.sh -m pdb aai.py -c config/aai-flask-testing-config.py 
# COORDS_ROOT not set. Using ..
# coords.so: ../Coordinates/Python/Boost/build/lib.macosx-10.13-x86_64-2.7/coords.so
# DYLD_LIBRARY_PATH :../Coordinates/libCoords
# PYTHONPATH :../Coordinates/Python/Boost/build/lib.macosx-10.13-x86_64-2.7:..

> /Users/lrm/src/starbug/AAI/www/aai.py(12)<module>()
-> """

(Pdb) b aai.factory
Breakpoint 1 at /Users/lrm/src/starbug/AAI/www/aai.py:28
(Pdb) c
> /Users/lrm/src/starbug/AAI/www/aai.py(37)factory()
-> config_key = 'AAI_FLASK_CONFIG'


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
