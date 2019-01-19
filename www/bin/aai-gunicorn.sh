#!/usr/bin/env bash
#
# This sets up the shell environment for gunicorn to find the wrapped coords library.
#

# I tried a bunch of things to pass both the gunicorn and flask config files:

# gunicorn -c $gunicorn_config_file 'aai:factory(${flask_config_file})'
# factory(${flask_config_file}) $ SyntaxError: invalid syntax

# gunicorn -c $gunicorn_config_file 'aai:factory(\${flask_config_file})'
# factory(${flask_config_file}) $ SyntaxError: invalid syntax

# gunicorn -c $gunicorn_config_file "aai:factory(${flask_config_file})"
# Failed to find application object 'factory(config/aai-flask-testing-config.py)' in 'aai'

# gunicorn -c $gunicorn_config_file 'aai:factory("${flask_config_file}")'
# IOError: [Errno 2] Unable to load configuration file (No such file or directory): '/opt/starbug.com/AAI/www/${flask_config_file}'

# gunicorn -c $gunicorn_config_file aai:factory("${flask_config_file}")
# /bin/aai-gunicorn.sh: line 143: syntax error near unexpected token `('

# gunicorn -c $gunicorn_config_file aai:factory\("${flask_config_file}"\)
# Failed to find application object 'factory(config/aai-flask-testing-config.py)' in 'aai'

# I decided to use an environment variable for AAI flask config for now.

# ----------------------
# ----- parse args -----
# ----------------------

# cli args from http://mywiki.wooledge.org/BashFAQ/035#getopts

show_help() {
cat << EOF
Usage: ${0##*/} [-h] [-f FLASK CONFIG FILE] [-g GUNICORN CONFIG FILE]

Passes a flask config file to the AAI flask framework and a gunicorn
config file to the gunicorn framework.

    -h                       display this help and exit
    -f FLASK_CONFIG_FILE     Flask configuration file
    -g GUNICORN_CONFIG_FILE  Gunicorn configuration file

EOF
}

die() {
    printf '%s\n' "$1" >&2
    exit 1
}

# Initialize all the option variables.
# This ensures we are not contaminated by variables from the environment.

gunicorn_config_file=
flask_config_file=


while :; do
    case $1 in
	-h|-\?|--help)
	    show_help    # Display a usage synopsis.
	    exit
	    ;;


	-f|--flask-file)       # Takes an option argument; ensure it has been specified.
	    if [ "$2" ]; then
		flask_config_file=$2
		shift
	    else
		die 'ERROR: "--flask-file" requires a non-empty option argument.'
	    fi
	    ;;
	--flask-file=?*)
	    flask_config_file=${1#*=} # Delete everything up to "=" and assign the remainder.
	    ;;
	--flask-file=)         # Handle the case of an empty --file=
	    die 'ERROR: "--flask-file" requires a non-empty option argument.'
	    ;;


	-g|--gunicorn-file)       # Takes an option argument; ensure it has been specified.
	    if [ "$2" ]; then
		gunicorn_config_file=$2
		shift
	    else
		die 'ERROR: "--gunicorn-file" requires a non-empty option argument.'
	    fi
	    ;;
	--gunicorn-file=?*)
	    gunicorn_config_file=${1#*=} # Delete everything up to "=" and assign the remainder.
	    ;;
	--gunicorn-file=)         # Handle the case of an empty --file=
	    die 'ERROR: "--gunicorn-file" requires a non-empty option argument.'
	    ;;


	-?*)
	    printf 'WARN: Unknown option (ignored): %s\n' "$1" >&2
	    ;;
	*)               # Default case: No more options, so break out of the loop.
	    break
    esac

    shift
done


if [ -z "$flask_config_file" ]; then
    echo '# AAI warning: no flask config file provided.'
    echo '# AAI_FLASK_CONFIG:' $AAI_FLASK_CONFIG
else
    echo '# AAI gunicorn wrapper ignoring flask config file:' $flask_config_file
fi


if [ -z "$gunicorn_config_file" ]; then
    die 'AAI ERROR: a gunicorn config file is required'
else
    echo '# AAI gunicorn config file:' $gunicorn_config_file
fi

echo '#' # linefeed

# ===========================
# ===== run application =====
# ===========================

. ./bin/setenv.sh

echo "# Starting gunicorn"

gunicorn -c $gunicorn_config_file "aai:factory()"
