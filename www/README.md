# SunPosition Web UI using Flask

This is the initial Web UI for my astronomy tool kit. I use
[Flask](http://flask.pocoo.org) to create the templates for the sun
position calculation.

# From the command line

## Setup pyenv

```
lrm@lrmz-iMac AAI (master)]$ pwd
/Users/lrm/src/starbug/AAI

[lrm@lrmz-iMac AAI (master)]$ mkdir pyenv

[lrm@lrmz-iMac AAI (master)]$ virtualenv pyenv
New python executable in /Users/lrm/src/starbug/AAI/pyenv/bin/python
Installing setuptools, pip, wheel...done.

[lrm@lrmz-iMac AAI (master)]$ source pyenv/bin/activate
(pyenv) [lrm@lrmz-iMac AAI (master)]$ pip list
DEPRECATION: The default format will switch to columns in the future. You can use --format=(legacy|columns) (or define a format=(legacy|columns) in your pip.conf under the [list] section) to disable this warning.
pip (9.0.1)
setuptools (38.2.4)
wheel (0.30.0)


(pyenv) [lrm@lrmz-iMac AAI (master)]$ pip list
DEPRECATION: The default format will switch to columns in the future. You can use --format=(legacy|columns) (or define a format=(legacy|columns) in your pip.conf under the [list] section) to disable this warning.
pip (9.0.1)
setuptools (38.2.4)
wheel (0.30.0)


(pyenv) [lrm@lrmz-iMac AAI (master)]$ pip install flask
Collecting flask
  Using cached Flask-0.12.2-py2.py3-none-any.whl
Collecting Jinja2>=2.4 (from flask)
  Using cached Jinja2-2.10-py2.py3-none-any.whl
Collecting Werkzeug>=0.7 (from flask)
  Using cached Werkzeug-0.13-py2.py3-none-any.whl
Collecting click>=2.0 (from flask)
  Using cached click-6.7-py2.py3-none-any.whl
Collecting itsdangerous>=0.21 (from flask)
  Using cached itsdangerous-0.24.tar.gz
Collecting MarkupSafe>=0.23 (from Jinja2>=2.4->flask)
  Using cached MarkupSafe-1.0.tar.gz
Building wheels for collected packages: itsdangerous, MarkupSafe
  Running setup.py bdist_wheel for itsdangerous ... done
  Stored in directory: /Users/lrm/Library/Caches/pip/wheels/fc/a8/66/24d655233c757e178d45dea2de22a04c6d92766abfb741129a
  Running setup.py bdist_wheel for MarkupSafe ... done
  Stored in directory: /Users/lrm/Library/Caches/pip/wheels/88/a7/30/e39a54a87bcbe25308fa3ca64e8ddc75d9b3e5afa21ee32d57
Successfully built itsdangerous MarkupSafe
Installing collected packages: MarkupSafe, Jinja2, Werkzeug, click, itsdangerous, flask
Successfully installed Jinja2-2.10 MarkupSafe-1.0 Werkzeug-0.13 click-6.7 flask-0.12.2 itsdangerous-0.24


(pyenv) [lrm@lrmz-iMac AAI (master)]$ pip list --format=columns
Package      Version
------------ -------
click        6.7
Flask        0.12.2
itsdangerous 0.24
Jinja2       2.10
MarkupSafe   1.0
pip          9.0.1
setuptools   38.2.4
Werkzeug     0.13
wheel        0.30.0


```

## Run pylanuch.sh

```

(pyenv) [lrm@lrmz-iMac www (master)]$ ./bin/pylaunch.sh aai.py --help
# COORDS_ROOT not set. Using ..
# coords.so: ../Coordinates/Python/Boost/build/lib.macosx-10.13-intel-2.7/coords.so
# DYLD_LIBRARY_PATH :../Coordinates/libCoords
# PYTHONPATH :../Coordinates/Python/Boost/build/lib.macosx-10.13-intel-2.7:..

usage: aai.py [-h] [-d] [--host host] [--logfilename logfilename]
	      [--loghandler HANDLER] [-l LEVEL] [-p PORT]

vArmour simple flask server

optional arguments:
  -h, --help            show this help message and exit
  -d, --debug           flask debug (default: False)
  --host host           host IP to serve (default: 0.0.0.0)
  --logfilename logfilename
			name of log file (default:
			/opt/starbug.com/logs/flask)
  --loghandler HANDLER  logging handler choice: rotating, stream (default:
			stream)
  -l LEVEL, --loglevel LEVEL
			logging level choice: debug, info, warn, error
			(default: warn)
  -p PORT, --port PORT  port (default: 8080)

```


# Docker install

See ../Dockerfile.flask

# Manual Apache Install

Originally this was installed manually on a system running Apache.
It has been superseded by the Docker install, but for the record:

If it isn't already installed:

```
sudo easy_install pip
```

then

```
sudo pip install Flask
```

## To Run from the command line

```
$ ./pylaunch.sh SunPosition.py
# COORDS_ROOT not set. Using ..
# coords.so: ../Coordinates/Python/Manual/build/lib.macosx-10.10-intel-2.7/coords.so
# DYLD_LIBRARY_PATH :../Coordinates/libCoords
# PYTHONPATH :../Coordinates/Python/Manual/build/lib.macosx-10.10-intel-2.7:..

 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

## To Debug

Set app.debug = True, but remember to turn it off in production since
it is a security issue.


## To run in Apache

On a CentOS system, you will need these packages:

### Yum Packages

```
sudo yum update -y

sudo yum groupinstall -y "Web Server"

sudo yum install httpd-devel -y
sudo yum install mod_wsgi -y

sudo yum install gcc -y
sudo yum install gcc-c++ -y
sudo yum install gdb -y
sudo yum install boost -y
sudo yum install boost-devel -y

sudo yum install gtest -y
sudo yum install gtest-devel -y

sudo yum install emacs -y

sudo yum install git -y

sudo pip install flask
```

### Configure Apache

To end of /etc/httpd/conf/httpd.conf, add these lines, with the
location were you have checked out this repo, /opt/starbug.com/AAI in
this case.

```
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
```

And one small hack for user apache to open a socket (see
/etc/httpd/logs/error_log if this does not start).

```
sudo chmod -R 775 /var/log/httpd
```

TODO: right way to do this.

### Install AAI

Get the aai repo from github and follow the steps below.

```
sudo -s
cd /opt/starbug.com

git clone https://github.com/lrmcfarland/AAI.git

cd AAI/
git submodule update --init --recursive

cd Coordinates/
./build.sh test

cd ../Transforms
./test_Transforms.sh

cd ../Bodies
./test_Bodies.sh

```

## Start Service

Use the service commands to control

```
sudo service httpd start
sudo service httpd restart
sudo service httpd stop
```
look for errors in

```
sudo cat /etc/httpd/logs/error_log

```
