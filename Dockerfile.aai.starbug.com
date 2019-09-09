# This is the starbug.com implementation of Astronomical Algorithms by Meeus
#
# This will build the aai app in a container and served by gunicorn.
# For use with nginx as a reverse proxy.
#
# with docker compose after building image (below)
#
# docker-compose -f aai-compose.yaml up -d
# docker-compose -f aai-compose.yaml down
#
# with just docker
#
# Assmues: starbug.com container rotates all logs and log name is unique. See CMD below.
#
# one time setup
# create network:      docker network create starbugnet
# persistent storage:  docker volume create starbuglogs
#                      docker volume create starbugconfig
#
# to build:            docker build -f Dockerfile.aai.starbug.com -t aai.starbug.com .
#
# WARNING: -p ports must match config file
#
# to run default flask:     docker run --net starbugnet --name aai.starbug.com_00 --mount source=starbugconfig,target=/opt/starbug.com/config --mount source=starbuglogs,target=/opt/starbug.com/logs -d -p 8080:8080 aai.starbug.com
#
# to run deploy flask:      docker run --net starbugnet --name aai.starbug.com_00 --mount source=starbugconfig,target=/opt/starbug.com/config --mount source=starbuglogs,target=/opt/starbug.com/logs -d -e AAI_FLASK_CONFIG='/opt/starbug.com/config/aai-flask-deployment-config.py' -p 8080:8080 aai.starbug.com
#
#
# to bash starbuglogs:       docker exec -it aai.starbug.com_00 bash
#
# to stop:                   docker stop aai.starbug.com_00
# to delete container:       docker rm aai.starbug.com_00
# to delete image:           docker rmi aai.starbug.com
#
# to tag:                    docker tag aai.starbug.com lrmcfarland/aai.starbug.com
# to push to dockerhub:      docker push lrmcfarland/aai.starbug.com
#
# to view docker logs:       docker logs aai.starbug.com_00
# to run bash:               docker run -it --entrypoint /bin/bash aai.starbug.com
#
# to delete all containers:  docker rm $(docker ps -a -q)
# to delete all images:      docker rmi $(docker images -q)
# to delete dangling images: docker rmi $(docker images -q -f dangling=true)

FROM centos

LABEL maintainer "lrm@starbug.com"
LABEL service "Astronomical Algorithms Implemented gunicorn wrapper"

# packages

RUN yum update -y
RUN yum install -y gcc gcc-c++ boost boost-devel make cmake git epel-release
RUN yum install -y python-devel python-pip && yum clean all # pip line belown not happy if this is in line above

COPY requirements.txt /tmp
RUN pip install --upgrade pip && pip install -r /tmp/requirements.txt

# --------------------
# ----- AAI home -----
# --------------------

ENV AAI_HOME="/opt/starbug.com" \
    AAI_USER="starbug" \
    AAI_GRP="starbug"

RUN groupadd ${AAI_GRP} \
    && adduser -g ${AAI_GRP} ${AAI_USER} \
    && mkdir -p ${AAI_HOME}/logs \
    && mkdir -p ${AAI_HOME}/config \
    && chown -R ${AAI_USER}:${AAI_GRP} ${AAI_HOME}

USER ${AAI_USER}:${AAI_GRP}

WORKDIR ${AAI_HOME}

# built with git
RUN git clone --recurse-submodules https://github.com/lrmcfarland/AAI.git

WORKDIR ${AAI_HOME}/AAI/

# WARNING: set the branch here if not using master, but don't forget
# to comment it out before merging back.
# RUN git checkout moon-position-v7
# RUN git submodule update --init --recursive

# -----------------
# ----- build -----
# -----------------

WORKDIR ${AAI_HOME}/AAI/Coordinates
RUN ./build.sh # optional test

# -----------------------
# ----- run web app -----
# -----------------------

COPY www/config/aai-flask-testing-config.py ${AAI_HOME}/AAI/www/config
COPY www/config/aai-gunicorn-config.py ${AAI_HOME}/AAI/www/config

WORKDIR ${AAI_HOME}/AAI/www

ENTRYPOINT ["bash"]

# Set the environment variable AAI_FLASK_CONFIG is set if not using
#  the default for example: -e AAI_FLASK_CONFIG='config/aai-flask-deployment-config.py'

CMD [ "./bin/aai-gunicorn.sh", "-g", "config/aai-gunicorn-config.py"]
