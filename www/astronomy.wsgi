"""astronomy wsgi wrapper for apache"""


import sys

# TODO fix hardcoded paths

sys.path.insert(0, '/var/www/Astronomy/Coordinates/Python/Boost/build/lib.linux-x86_64-2.7')
sys.path.insert(0, '/var/www/Astronomy')
sys.path.insert(0, '/var/www/Astronomy/www')

from astronomy import app as application
