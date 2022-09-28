bind = '0.0.0.0:8000'
workers = 2
chdir = '/app/webthingstalk'
loglevel = 'debug'
accesslog = '/var/log/access_log_webthingstalk'
acceslogformat = "%(h)s %(l)s %(u)s %(t)s %(r)s %(s)s %(b)s %(f)s %(a)s"
errorlog = '/var/log/error_log_webthingstalk'