from apps import app
from workers import wsgi

Default = wsgi.entrypoint(app)
