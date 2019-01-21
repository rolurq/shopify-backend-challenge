from .gunicorn import *

loglevel = "warning"
errorlog = "logs/error.log"
pidfile = "pid"
daemon = True
