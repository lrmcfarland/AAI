#!/usr/bin/env bash
#
# Sets up environment for flask to run AAI
#
# To run (in the directory above):
#
#     ./bin/aai-flask.sh -f config/aai-flask-testing-config.py
#


show_help() {
cat << EOF
Usage: ${0##*/} [-h] [-f FLASK CONFIG FILE]

Passes a flask config file to the AAI flask framework

    -h                       display this help and exit
    -f FLASK_CONFIG_FILE     Flask configuration file

EOF
}

die() {
    printf '%s\n' "$1" >&2
    exit 1
}

# Initialize all the option variables.
# This ensures we are not contaminated by variables from the environment.

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


	-?*)
	    printf 'WARN: Unknown option (ignored): %s\n' "$1" >&2
	    ;;
	*)               # Default case: No more options, so break out of the loop.
	    break
    esac

    shift
done



# ===========================
# ===== run application =====
# ===========================

# This sets up the shell environment for flask to find the wrapped coords library.
. ./bin/setenv.sh


if [ -z "$flask_config_file" ]; then
    echo 'AAI warning: no flask config file provided.'
    python ./aai.py
else
    # -f becomes -c in aai.py
    python ./aai.py -c $flask_config_file
fi
