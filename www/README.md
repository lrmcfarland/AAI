# SunPosition Web UI using Flask

## [Flask](http://flask.pocoo.org)



## To Install

On older pythons with out pip installed:

```
sudo easy_install pip
```

then

```
sudo pip install Flask
```

## To Run

```
$ ./pylaunch.sh SunPosition.py
# COORDS_ROOT not set. Using ..
# coords.so: ../Coordinates/Python/Manual/build/lib.macosx-10.10-intel-2.7/coords.so
# DYLD_LIBRARY_PATH :../Coordinates/libCoords
# PYTHONPATH :../Coordinates/Python/Manual/build/lib.macosx-10.10-intel-2.7:..

 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

## To Debug

```
if __name__ == "__main__":

    app.debug = True # TODO Security HOLE!!!

```


## Apache


### Add Yum Packages

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


Install Astronomy 


sudo -s
cd /var/www

git clone https://github.com/lrmcfarland/Astronomy.git
cd Astronomy/
git submodule update --init --recursive
cd Coordinates/
./build.sh test

```

this on the mod_wsgi branch at this time 2015sep21


### Configure Apache

add to end of /etc/httpd/conf/httpd.conf

```
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
```


Start Service

```
sudo service httpd start
sudo service httpd restart
sudo service httpd stop
```
look for errors in 

```
sudo cat /etc/httpd/logs/error_log

[Tue Sep 22 04:20:37 2015] [error] [client 50.131.221.92] (13)Permission denied: mod_wsgi (pid=3302): Unable to connect to WSGI daemon process 'astronomy' on '/etc/httpd/logs/wsgi.3299.0.1.sock' after multiple attempts.


sudo chmod -R 775 /var/log/httpd
```

works!

TODO too open? add www group?






