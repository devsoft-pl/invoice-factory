wsgi_app = "base.wsgi:application"
bind = "0.0.0.0:8000"
raw_env = ["DJANGO_SETTINGS_MODULE=base.settings.production"]
chdir = "/app"
loglevel = "INFO"
workers = 2
threads = 5

timeout = 60  # tmp
keepalive = 30
