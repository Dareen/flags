FROM jeethu/baseimage-pypy:0.9.16.1

MAINTAINER Dareen Alhiyari <dareen@dubizzle.com>

ENV USER             dubizzle
ENV GROUP            $USER
ENV USER_DIR         /home/$USER
ENV VENV_DIR         $USER_DIR/webapps/flags_env
ENV REPO_DIR         $VENV_DIR/flags
ENV VENV_PYTHON      $VENV_DIR/bin/python
ENV VENV_PIP         $VENV_DIR/bin/pip
ENV USER_LOGGING_DIR /var/log/$USER

# Install System Packages
# TODO: filter those packages to only what's needed
RUN set -e; \
    add-apt-repository ppa:chris-lea/nginx-devel; \
    apt-get update -y; \
    apt-get install -y nginx gcc

ADD requirements.txt /tmp/

# Set User and Group
RUN set -e; \
    useradd -m -d /home/$USER -p $USER -s /bin/bash $USER; \
    chown -R $USER:$USER $USER_DIR; \
    mkdir -p $USER_LOGGING_DIR; \
    chmod a+rw -R $USER_LOGGING_DIR; \
    su - $USER -l -c "virtualenv-pypy $VENV_DIR"; \
    su - $USER -l -c "$VENV_PIP install --upgrade -r /tmp/requirements.txt"; \
    su - $USER -l -c "rm -rf $USER_DIR/.cache/pip/wheels"

ADD archive.tar.gz $REPO_DIR

RUN set -e; \
    chown -R dubizzle:dubizzle $VENV_DIR; \
    rm /etc/nginx/sites-enabled/default; \
    ln -sf $REPO_DIR/deploy/uwsgi_params /etc/nginx/uwsgi_params; \
    mkdir -p /etc/service/flags_uwsgi; \
    mkdir -p /etc/service/nginx; \
    mkdir -p /var/log/dubizzle; \
    cp $REPO_DIR/docker/services/uwsgi.sh /etc/service/flags_uwsgi/run; \
    cp $REPO_DIR/docker/services/nginx.sh /etc/service/nginx/run; \
    chmod +x /etc/service/flags_uwsgi/run; \
    chown $USER:$USER -R /var/log/dubizzle; \
    chmod +x /etc/service/nginx/run

EXPOSE 80 8090

CMD ["/sbin/my_init"]
