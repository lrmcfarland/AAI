# SunPosition Web UI using Flask

## [Flask](http://flask.pocoo.org)



## To Install

On older pythons with out pip installed:

```
sudo easy_install pip
```

then

```
sudo pip install Flask
```

## To Run

```
$ ./pylaunch.sh SunPosition.py
# COORDS_ROOT not set. Using ..
# coords.so: ../Coordinates/Python/Manual/build/lib.macosx-10.10-intel-2.7/coords.so
# DYLD_LIBRARY_PATH :../Coordinates/libCoords
# PYTHONPATH :../Coordinates/Python/Manual/build/lib.macosx-10.10-intel-2.7:..

 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

## To Debug

```
if __name__ == "__main__":

    app.debug = True # TODO Security HOLE!!!

```


