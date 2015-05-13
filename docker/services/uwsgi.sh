#!/bin/bash
chmod a+r /etc/container_environment.sh
source /etc/container_environment.sh

/bin/sed -i "s/__SYSLOG_HOST__/${SYSLOG_HOST}/g" $REPO_DIR/deploy/flags.ini
/bin/sed -i "s/__SYSLOG_PORT__/${SYSLOG_PORT}/g" $REPO_DIR/deploy/flags.ini

exec /sbin/setuser dubizzle $VENV_DIR/bin/uwsgi --ini $REPO_DIR/deploy/flags.ini
