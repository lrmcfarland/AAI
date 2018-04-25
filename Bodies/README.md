# Bodies

This contains implementations of algorithms for the position of celestial bodies like the sun.

# Test

## Set up the python environment

```
$ virtualenv pyenv
$ source ~/pyenv/bin/activate
$ (pyenv) pip install -r requirements.txt
```

## Run with the pylaunch.sh wrapper

```
$ cd www

(pyenv) $ ./pylaunch.sh test_SunPosition.py 
# COORDS_ROOT not set. Using ..
# coords.so: ../Coordinates/Python/Boost/build/lib.macosx-10.13-intel-2.7/coords.so
# DYLD_LIBRARY_PATH :../Coordinates/libCoords
# PYTHONPATH :../Coordinates/Python/Boost/build/lib.macosx-10.13-intel-2.7:..

..................F.......s

```

# Debug

You can use the python debugger in unit test, but need the python path in pylaunch.sh to run.
To set a break point by module step through until the module is imported.
Otherwise, use the file and line number.

## Breakpoint by file

```

(pyenv) [rmcfarland@VSN00249 Bodies (day-off-rise-set)]$ ./pylaunch.sh -m pdb test_SunPosition.py -v SunRiseAndSetTests.test_mlc_2018apr22_0600
# COORDS_ROOT not set. Using ..
# coords.so: ../Coordinates/Python/Boost/build/lib.macosx-10.12-x86_64-2.7/coords.so
# DYLD_LIBRARY_PATH :../Coordinates/libCoords
# PYTHONPATH :../Coordinates/Python/Boost/build/lib.macosx-10.12-x86_64-2.7:..

> /Users/rmcfarland/src.old/starbug/AAI/Bodies/test_SunPosition.py(15)<module>()
-> """
(Pdb) b SunPosition.py:317
Breakpoint 1 at /Users/rmcfarland/src.old/starbug/AAI/Bodies/SunPosition.py:317

(Pdb) c
test_mlc_2018apr22_0600 (__main__.SunRiseAndSetTests)
Test for setting off by a day in the old algorithm ... > /Users/rmcfarland/src.old/starbug/AAI/Bodies/SunPosition.py(317)RiseAndSet()
-> if not a_datetime.timezone:


(Pdb) p str(rising_loc)
'2018-04-21T13:28:33.2722-08'

(Pdb) p rising_loc.toJulianDate() - a_datetime.toJulianDate()
-0.6885037934407592


```

## Breakpoint by object

You must next to the import first.

```
(pyenv) [lrm@lrmz-iMac Bodies (master)]$ ./pylaunch.sh -m pdb test_SunPosition.py -v SunRiseAndSetTests.test_mlc_2018apr20_1800
# COORDS_ROOT not set. Using ..
# coords.so: ../Coordinates/Python/Boost/build/lib.macosx-10.13-intel-2.7/coords.so
# DYLD_LIBRARY_PATH :../Coordinates/libCoords
# PYTHONPATH :../Coordinates/Python/Boost/build/lib.macosx-10.13-intel-2.7:..

> /Users/lrm/src/starbug/AAI/Bodies/test_SunPosition.py(15)<module>()
-> """
(Pdb) n
> /Users/lrm/src/starbug/AAI/Bodies/test_SunPosition.py(17)<module>()
-> import math
(Pdb) n
> /Users/lrm/src/starbug/AAI/Bodies/test_SunPosition.py(18)<module>()
-> import time
(Pdb) n
> /Users/lrm/src/starbug/AAI/Bodies/test_SunPosition.py(19)<module>()
-> import unittest
(Pdb) n
> /Users/lrm/src/starbug/AAI/Bodies/test_SunPosition.py(21)<module>()
-> import coords
(Pdb) n
> /Users/lrm/src/starbug/AAI/Bodies/test_SunPosition.py(22)<module>()
-> import SunPosition

(Pdb) b SunPosition.RiseAndSet


(Pdb) c
test_mlc_2018apr20_1800 (__main__.SunRiseAndSetTests)
Test for in august ... > /Users/lrm/src/starbug/AAI/Bodies/SunPosition.py(235)RiseAndSet()
-> JD, JDo = Transforms.SiderealTime.USNO_C163.JulianDate0(a_datetime)
(Pdb) n


(Pdb) p str(transit_utc)
'2018-04-20T20:08:54.917'
(Pdb) p str(transit_loc)
'2018-04-20T12:08:54.917-08'


(Pdb) p str(rising_loc)
'2018-04-20T05:28:33.0581-08'
(Pdb) p rising_loc.toJulianDate()
2458228.394827061
(Pdb) p a_datetime.toJulianDate()
2458228.9166666665



(Pdb) rising_loc.toJulianDate() - a_datetime.toJulianDate()
-0.5218396056443453




(Pdb) b 328
Breakpoint 2 at /Users/lrm/src/starbug/AAI/Bodies/SunPosition.py:328




```


