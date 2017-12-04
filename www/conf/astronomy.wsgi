"""astronomy wsgi wrapper for Apache

This is superseded by the docker install.

Originally this assumed this is installed in /var/www/Astronomy/www/astronomy.wsgi and hard coded in /etc/httpd/conf/httpd.conf as

<VirtualHost *>
    ServerName astarbug.com

    WSGIDaemonProcess astronomy user=apache group=apache threads=5
    WSGIScriptAlias / /var/www/Astronomy/www/astronomy.wsgi

    <Directory /var/www/Astronomy/www>
        WSGIProcessGroup astronomy
        WSGIApplicationGroup %{GLOBAL}
        Order deny,allow
        Allow from all
    </Directory>
</VirtualHost>


"""


import sys

# TODO fix hard coded paths

sys.path.insert(0, '/var/www/Astronomy/Coordinates/Python/Boost/build/lib.linux-x86_64-2.7')
sys.path.insert(0, '/var/www/Astronomy')
sys.path.insert(0, '/var/www/Astronomy/www')

from astronomy import app as application
