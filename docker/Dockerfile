FROM        phusion/baseimage:0.9.15

MAINTAINER  Dareen Alhiyari <dareen@dubizzle.com>

ENV         USER                    dubizzle
ENV         GROUP                   $USER
ENV         USER_DIR                /home/$USER
ENV         VENV_DIR                $USER_DIR/webapps/flags_env
ENV         REPO_DIR                $VENV_DIR/flags
ENV         VENV_PYTHON             $VENV_DIR/bin/python
ENV         VENV_PIP                $VENV_DIR/bin/pip
ENV         USER_LOGGING_DIR        /var/log/$USER


ADD         requirements.txt /tmp/

# Install System Packages
# TODO: filter those packages to only what's needed
RUN         set -e && \
            add-apt-repository ppa:chris-lea/nginx-devel && \
            apt-get update -y && \
            apt-get install -y make \
                libcurl4-openssl-dev \
                python2.7-dev \
                python-virtualenv  \
                vim \
                curl \
                nginx \
                libxft2 \
                libfreetype6 \
                zlib1g-dev \
                gettext \
                libffi-dev \
                libevent-dev \
                httperf \
                libpng12-dev \
                libjpeg62-dev \
                zlibc \
                libfreetype6-dev \
                python-setuptools

# Set User and Group
RUN         useradd -m -d /home/$USER -p $USER -s /bin/bash $USER && \
            chown -R $USER:$USER $USER_DIR && \
            mkdir -p $USER_LOGGING_DIR && \
            chmod oug+rw -R $USER_LOGGING_DIR

ADD         archive.tar.gz $REPO_DIR

# Install Python Packages in Virtual Environment
RUN chown -R $USER:$USER $USER_DIR && \
    su - $USER -l -c "virtualenv --system-site-packages $VENV_DIR" && \
    su - $USER -l -c "$VENV_PIP install --upgrade -r $REPO_DIR/requirements/base.txt"

RUN set -e && \
    chown -R dubizzle:dubizzle $VENV_DIR && \
    rm /etc/nginx/sites-enabled/default && \
    ln -sf $REPO_DIR/deploy/uwsgi_params /etc/nginx/uwsgi_params && \
    mkdir -p /etc/service/flags_uwsgi && \
    mkdir -p /etc/service/nginx && \
    mkdir -p /var/log/dubizzle && \
    cp $REPO_DIR/docker/services/uwsgi.sh /etc/service/flags_uwsgi/run; \
    cp $REPO_DIR/docker/services/nginx.sh /etc/service/nginx/run; \
    chmod +x /etc/service/flags_uwsgi/run; \
    chown $USER:$USER -R /var/log/dubizzle; \
    chmod +x /etc/service/nginx/run

EXPOSE 80 8090

CMD ["/sbin/my_init"]
