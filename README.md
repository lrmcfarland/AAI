# Astronomy

This a collection of my implementations of various algorithms I found
on line and in books, in particular
[Astronomical Algorithms](http://www.willbell.com/math/mc1.htm)
by [Jean Meeus](https://en.wikipedia.org/wiki/Jean_Meeus)

I use this to collect my thoughts about various programming problems into
a coherent whole in service of an application.

I started with some object oriented ideas about using C++ to
build a [Coordinates library](https://github.com/lrmcfarland/Coordinates)
to do basic physics.
I use the operator overloading feature of C++ to abstract away the vector
arithmatic and focus on the physics.
I back this up with a full set of unit tests.

Next I investigated wrapping these C++ objects in python.
They are too small for this to be much of a performance advantage,
but I wanted to see how hard it would be to bring in more complex C++ libraries
(and I have wrapped FORTRAN in C++ before too ... )
Besides making it more fun to play with, I can use Python frameworks like
[flask](https://en.wikipedia.org/wiki/Flask_(web_framework)) to provide a browser UI.

Finally, adding nginx as a reverse proxy and TLS end point (to use
the geolocation features of the browser) as a Docker micro-service.
At 700MB it is a really fat micro service needing a multi stage diet soon,
but thats why I am doing this.

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
in latitude, longitude and date-time. It is available on [aai.starbug.com](https://aai.starbug.com).
Here are some screen shots:

## San Franciso 2017-11-19

![San Francisco 2017-11-19](https://github.com/lrmcfarland/Astronomy/blob/master/images/san-francisco-2017-11-19.png?raw=true)

## Syene on the summer solstice

This is [Syene](https://en.wikipedia.org/wiki/Aswan) at noon on the summer
solstice when the sun is directly overhead and casts no shadow in a deep well.
[Eratosthenes](https://en.wikipedia.org/wiki/Eratosthenes#Measurement_of_the_Earth.27s_circumference)
used this observation to calculate the Earth's circumference.

![Aswan 2017-11-19](https://github.com/lrmcfarland/Astronomy/blob/master/images/aswan-2017-06-21.png?raw=true)

## TODO Stonehenge Manhattenhenge

[Equation of Time](https://en.wikipedia.org/wiki/Equation_of_time)

![Equation of Time](https://github.com/lrmcfarland/Astronomy/blob/master/images/eot_2015.png?raw=true)


[Analemma](https://en.wikipedia.org/wiki/Analemma)

![Analemma](https://github.com/lrmcfarland/Astronomy/blob/master/images/analemma_45N.png?raw=true)




# Moon Position


Lunar Altitude

![Lunar Altitude](https://github.com/lrmcfarland/Astronomy/blob/master/images/lunar_altitude_20150429.png?raw=true)
