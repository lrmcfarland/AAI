"""aai wsgi wrapper for Apache

This is superseded by the docker install.

Originally this assumed this is installed in /opt/starbug.com/AAI/www/aai.wsgi and hard coded in /etc/httpd/conf/httpd.conf as

<VirtualHost *>
    ServerName astarbug.com

    WSGIDaemonProcess aai user=apache group=apache threads=5
    WSGIScriptAlias / /opt/starbug.com/AAI/www/aai.wsgi

    <Directory /opt/starbug.com/AAI/www>
        WSGIProcessGroup aai
        WSGIApplicationGroup %{GLOBAL}
        Order deny,allow
        Allow from all
    </Directory>
</VirtualHost>


"""


import sys

# TODO fix hard coded paths

sys.path.insert(0, '/opt/starbug.com/AAI/Coordinates/Python/Boost/build/lib.linux-x86_64-2.7')
sys.path.insert(0, '/opt/starbug.com/AAI')
sys.path.insert(0, '/opt/starbug.com/AAI/www')

from aai import app as application
