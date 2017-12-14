# SunPosition Web UI using Flask

This is the initial Web UI for my astronomy tool kit. I use
[Flask](http://flask.pocoo.org) to create the templates for the sun
position calculation.

## Docker install

See ../Dockerfile.flask

## Manual Apache Install

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

### To Run from the command line

```
$ ./pylaunch.sh SunPosition.py
# COORDS_ROOT not set. Using ..
# coords.so: ../Coordinates/Python/Manual/build/lib.macosx-10.10-intel-2.7/coords.so
# DYLD_LIBRARY_PATH :../Coordinates/libCoords
# PYTHONPATH :../Coordinates/Python/Manual/build/lib.macosx-10.10-intel-2.7:..

 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

### To Debug

Set app.debug = True, but remember to turn it off in production since
it is a security issue.


### To run in Apache

On a CentOS system, you will need these packages:

#### Yum Packages

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

#### Configure Apache

To end of /etc/httpd/conf/httpd.conf, add these lines, with the
location were you have checked out this repo, /var/www/AAI in
this case.

```
<VirtualHost *>
    ServerName astarbug.com

    WSGIDaemonProcess aai user=apache group=apache threads=5
    WSGIScriptAlias / /var/www/AAI/www/aai.wsgi

    <Directory /var/www/AAI/www>
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

#### Install AAI

Get the aai repo from github and follow the steps below.

```
sudo -s
cd /var/www

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

### Start Service

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
