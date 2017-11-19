# Astronomy

This a collection of my implementations of various algorithms I found
on line and in books, in particular
[Astronomical Algorithms](http://www.willbell.com/math/mc1.htm)
by [Jean Meeus](https://en.wikipedia.org/wiki/Jean_Meeus)

It serves as a test bed for my
[Coordinates](https://github.com/lrmcfarland/Coordinates)
library by using it as a submodule.

Results are validated with [NOAA's
solcalc](http://www.esrl.noaa.gov/gmd/grad/solcalc/) and using my
[Davis Mark 15
sextant](http://www.landfallnavigation.com/-nd026.html?cmp=froogle&kw=-nd026&utm_source=-nd026&utm_medium=shopping%2Bengine&utm_campaign=froogle)
with a swimming pool as an artificial horizon.
Details are recorded in the [unit tests](https://github.com/lrmcfarland/Astronomy/blob/master/Bodies/test_SunPosition.py).

It is a work in progress.

# SunPosition

[SunPosition.py](https://github.com/lrmcfarland/Astronomy/blob/master/Bodies/SunPosition.py)
returns the position of the sun given the observer's location on earth
in latitude, longitude and date-time.

With this, I generated the following plots:


Solar Altitude

![Solar Altitude vs Time] (https://github.com/lrmcfarland/Astronomy/blob/master/Images/solar_altitude_vs_time.png)

![Solar Altitude vs Azimuth] (https://github.com/lrmcfarland/Astronomy/blob/master/Images/solar_altitude_vs_azimuth.png)


[Equation of Time](https://en.wikipedia.org/wiki/Equation_of_time)

![Equation of Time] (https://github.com/lrmcfarland/Astronomy/blob/master/Images/eot_2015.png)


[Analemma](https://en.wikipedia.org/wiki/Analemma)

![Analemma] (https://github.com/lrmcfarland/Astronomy/blob/master/Images/analemma_45N.png)




# Moon Position


Lunar Altitude

![Lunar Altitude] (https://github.com/lrmcfarland/Astronomy/blob/master/Images/lunar_altitude_20150429.png)
