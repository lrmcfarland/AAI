"""Unit tests for Sun Position calculations

to run:  ./pylaunch.sh test_SunPosition.py
verbose: ./pylaunch.sh test_SunPosition.py -v
filter:  ./pylaunch.sh test_SunPosition.py -v test_EoT_404MLC_2015_03_20T12_00
debug:   ./pylaunch.sh -m pdb test_SunPosition.py

next until import module:

(Pdb) n
> /Users/lrm/src/Astronomy/Transforms/test_SunPosition.py(25)<module>()
-> import SunPosition
(Pdb) b SunPosition.SunPosition.EquationOfTime
Breakpoint 1 at /Users/lrm/src/Astronomy/Transforms/SunPosition.py:17


"""

import math
import time
import unittest

import coords
import SunPosition

from Transforms import EclipticEquatorial
from Transforms import EquatorialHorizon


class SunPositionsTests(unittest.TestCase):
    """Test Sun Position calculations"""

    def setUp(self):
        """Set up test parameters."""

        self.places = 12

        self.an_observer = coords.spherical(1, coords.angle(37, 24), coords.angle(-122, 4, 56))


    def test_EoT_2015_01_01T12_00(self):
        """Test Equation of time 2015-01-01T12:00:00

        validate with http://www.esrl.noaa.gov/gmd/grad/solcalc/
        """

        a_datetime = coords.datetime(2015, 01, 01, 12)
        eot = SunPosition.EquationOfTime(a_datetime)

        # NOAA says -3.59 minutes
        self.assertAlmostEqual(-3.4317446135022323, eot.value*60, self.places)


    def test_EoT_2015_02_11T12_00(self):
        """Test Equation of time 2015-02-11T12:00:00

        first local minimum of the year

        validate with http://www.esrl.noaa.gov/gmd/grad/solcalc/
        """

        a_datetime = coords.datetime(2015, 02, 11, 12)
        eot = SunPosition.EquationOfTime(a_datetime)

        # NOAA says -14.24 minutes
        self.assertAlmostEqual(-14.212711856485711, eot.value*60, self.places)


    def test_EoT_2015_03_20T12_00(self):
        """Test Equation of time 2015-03-20T12:00:00

        validate with http://www.esrl.noaa.gov/gmd/grad/solcalc/
        """

        a_datetime = coords.datetime(2015, 03, 20, 12)
        eot = SunPosition.EquationOfTime(a_datetime)

        # NOAA says -7.44 minutes
        self.assertAlmostEqual(-7.563513810377245, eot.value*60, self.places)


    def test_EoT_2015_05_14T12_00(self):
        """Test Equation of time 2015-05-14T12:00:00

        first local maximum of the year

        validate with http://www.esrl.noaa.gov/gmd/grad/solcalc/
        """

        a_datetime = coords.datetime(2015, 05, 14, 12)
        eot = SunPosition.EquationOfTime(a_datetime)

        # NOAA says 3.65 minutes
        self.assertAlmostEqual(3.6588472510257475, eot.value*60, self.places)


    def test_EoT_2015_07_26T12_00(self):
        """Test Equation of time 2015-07-26T12:00:00

        second local minimum of the year

        validate with http://www.esrl.noaa.gov/gmd/grad/solcalc/
        """

        a_datetime = coords.datetime(2015, 07, 26, 12)
        eot = SunPosition.EquationOfTime(a_datetime)

        # NOAA says -6.54 minutes
        self.assertAlmostEqual(-6.5354183954768175, eot.value*60, self.places)



    def test_EoT_2015_11_03T12_00(self):
        """Test Equation of time 2015-11-03T12:00:00

        second local maximum of the year

        validate with http://www.esrl.noaa.gov/gmd/grad/solcalc/
        """

        a_datetime = coords.datetime(2015, 11, 03, 12)
        eot = SunPosition.EquationOfTime(a_datetime)

        # NOAA says 16.48 minutes
        self.assertAlmostEqual(16.43786410739647, eot.value*60, self.places)





if __name__ == '__main__':
    unittest.main()
