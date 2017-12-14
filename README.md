# Astronomy

This a collection of my implementations of various algorithms I found
on line and in books, in particular
[Astronomical Algorithms](http://www.willbell.com/math/mc1.htm)
by [Jean Meeus](https://en.wikipedia.org/wiki/Jean_Meeus)

I use this to collect what I learned about various programming problems into
a coherent whole in service of an application.

I started with some object oriented ideas about using C++ to build a
[Coordinates library](https://github.com/lrmcfarland/Coordinates) to
do basic physics but use Scott Meyer's Effective C++ and other
recommended techniques.
I use the operator overloading feature of C++
to abstract away the vector arithmetic and focus on the physics.  I
back this up with a full set of unit tests.

Next I investigated wrapping these C++ objects in python.
They are too small for this to be much of a performance advantage,
but I wanted to see how hard it would be to bring in more complex C++ libraries
(and I have wrapped FORTRAN in C++ before too ... )
Besides making it more fun to play with, I can use Python frameworks like
[flask](https://en.wikipedia.org/wiki/Flask_(web_framework)) to provide a browser UI.
That also opens the door for HTML, CSS, JavaScript, JSON, JQuery and Google charts.

Finally, adding nginx as a reverse proxy and TLS end point (to use
the geolocation features of the browser) as a Docker micro-service.
At 700MB it is a really fat micro service needing a multi stage diet soon,
but then again, that is the type of problem I am looking for in doing this.

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


## API



```
curl https://aai.starbug.com/api/v1/sun_position_data\?latitude=37\&longitude=-122\&date=2017-12-11\&time=14\%3A37\%3A54\&timezone=-8\&dst=false

{
  "altitude_data_24h": [
    [
      0,
      -53.12289141057474,
      -29.529772137731925,
      -52.545518554707144,
      -76.3762556772508,
      -75.96224706420884
    ],

...

  ],
  "datetime": "2017-12-11T14:37:54-08",
  "observer": "<spherical><r>1</r><theta>53</theta><phi>-122</phi></spherical>",
  "rising": "2017-12-11T07:12:13.2009-08",
  "setting": "2017-12-11T16:52:24.806-08",
  "sun_date_label": [
    "2017-12-11"
  ],
  "sun_marker_altitude": "19:33:0.925497 (19.5502570824)",
  "sun_marker_azimuth": "218:05:11.8683 (218.086630087)",
  "sun_marker_time": 14.631666675209999,
  "transit": "2017-12-11T12:02:19.0035-08"
}



curl https://aai.starbug.com/api/v1/radec2azalt?latitude=37.40012123209991\&longitude=-122.08225404051541\&date=2017-12-11\&time=21%3A42%3A05\&timezone=-8\&dst=false\&ra=0\&dec=0

{
  "altitude": 34.91958722761523,
  "azimuth": 237.74055887676423,
  "datetime": "2017-12-11T21:42:05-08",
  "observer": "<spherical><r>1</r><theta>52.5999</theta><phi>-122.082</phi></spherical>"
}




curl https://aai.starbug.com/api/v1/azalt2radec?latitude=37.40012123209991\&longitude=-122.08225404051541\&date=2017-12-11\&time=21%3A42%3A05\&timezone=-8\&dst=false\&azimuth=237.74055887676423\&altitude=34.91958722761523
{
  "datetime": "2017-12-11T21:42:05-08",
  "dec": 1.4210854715202004e-14,
  "observer": "<spherical><r>1</r><theta>52.5999</theta><phi>-122.082</phi></spherical>",
  "ra": 24.0
}

```

## San Franciso 2017-11-19

![San Francisco 2017-11-19](https://github.com/lrmcfarland/Astronomy/blob/master/images/san-francisco-2017-11-19.png?raw=true)

## Syene on the summer solstice

This is [Syene](https://en.wikipedia.org/wiki/Aswan) at noon on the summer
solstice when the sun is directly overhead and casts no shadow in a deep well.
[Eratosthenes](https://en.wikipedia.org/wiki/Eratosthenes#Measurement_of_the_Earth.27s_circumference)
used this observation to calculate the Earth's circumference.

![Aswan 2017-11-19](https://github.com/lrmcfarland/Astronomy/blob/master/images/aswan-2017-06-21.png?raw=true)

## Lillehammer

![lillehammer-2017-06-21.png](https://github.com/lrmcfarland/Astronomy/blob/master/images/lillehammer-2017-06-21.png?raw=true)


## TODO Stonehenge Manhattenhenge

## Other

Under development.

[Equation of Time](https://en.wikipedia.org/wiki/Equation_of_time)

![Equation of Time](https://github.com/lrmcfarland/Astronomy/blob/master/images/eot_2015.png?raw=true)


[Analemma](https://en.wikipedia.org/wiki/Analemma)

![Analemma](https://github.com/lrmcfarland/Astronomy/blob/master/images/analemma_45N.png?raw=true)

Lunar Altitude

![Lunar Altitude](https://github.com/lrmcfarland/Astronomy/blob/master/images/lunar_altitude_20150429.png?raw=true)
