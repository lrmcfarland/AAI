# This is the starbug.com implementation of Astronomical Algorithms by Meeus
#
# This will build the aai app in a container and served by gunicorn.
# For use with nginx as a reverse proxy.
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
# to run detached:     docker run -d --net starbugnet --name aai.starbug.com_00 --mount source=starbugconfig,target=/opt/starbug.com/config --mount source=starbuglogs,target=/opt/starbug.com/logs -p 8080:8080 aai.starbug.com
#
# interactive: docker run -it --net starbugnet --name aai.starbug.com_00 --mount source=starbugconfig,target=/opt/starbug.com/config --mount source=starbuglogs,target=/opt/starbug.com/logs -p 8080:8080 aai.starbug.com
#
# to deploy:           docker run -d --net starbugnet --name aai.starbug.com_00 --mount source=starbugconfig,target=/opt/starbug.com/config --mount source=starbuglogs,target=/opt/starbug.com/logs -e AAI_FLASK_CONFIG='/opt/starbug.com/config/aai-flask-deployment-config.py' -p 8080:8080 aai.starbug.com
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

# -----------------------
# ----- run web app -----
# -----------------------

COPY . ${AAI_HOME}/AAI/www/

WORKDIR ${AAI_HOME}/AAI/www


# RUN pip install --upgrade pip && pip install -r /tmp/requirements.txt


ENTRYPOINT ["bash"]

# Set the environment variable AAI_FLASK_CONFIG is set if not using
#  the default for example: -e AAI_FLASK_CONFIG='config/aai-flask-deployment-config.py'



# CMD [ "./bin/aai-gunicorn.sh", "-g", "config/aai-gunicorn-config.py"]
