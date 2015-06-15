#!/bin/bash
chmod a+r /etc/container_environment.sh
source /etc/container_environment.sh

# Generate the uwsgi ini file from template and the container environment.
su dubizzle -l -c "$VENV_DIR/bin/envtpl < $REPO_DIR/deploy/flags.ini.tpl > $REPO_DIR/deploy/flags.ini"

exec /sbin/setuser dubizzle $VENV_DIR/bin/uwsgi --ini $REPO_DIR/deploy/flags.ini
