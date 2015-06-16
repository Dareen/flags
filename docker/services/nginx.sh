#!/bin/bash

ln -sf /home/dubizzle/webapps/flags_env/flags/deploy/nginx.conf /etc/nginx/sites-enabled/flags.conf

exec /usr/sbin/nginx -c /etc/nginx/nginx.conf -g "daemon off;"
