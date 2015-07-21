[uwsgi]
socket = 127.0.0.1:8090
master = true
virtualenv = {{ VENV_DIR }}
pythonpath = {{ REPO_DIR }}
pypy-wsgi-file = server.py
logger = rsyslog:{{ SYSLOG_HOST | default("syslog-aws.dubizzlecloud.internal") }}:{{ SYSLOG_PORT | default("1122") }},{{ APP_NAME }}_uwsgi
logto = /var/log/dubizzle/{{ APP_NAME }}_uwsgi.log
processes = 4
threads = 2
stats = :1717
enable-thread = true
single-interpreter = true
lazy-apps = true
socket-timeout = 30
harakiri = 30
reload-on-as = 1024
evil-reload-on-as = 2048
die-on-term
# for newrelic
post-buffering = 20971520
buffer-size = 32768
