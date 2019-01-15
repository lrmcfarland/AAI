# aai gunicorn config

bind = "0.0.0.0:8080"
workers = 4

loglevel = 'info'

capture_output = True

errorlog = "/opt/starbug.com/logs/aai-error.log"
accesslog = "/opt/starbug.com/logs/aai-access.log"

forwarded_allow_ips = "*"
