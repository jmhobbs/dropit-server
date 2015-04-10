# -*- coding: utf-8 -*-

from flask import Flask

import extensions

from frontend import frontend
from upload import upload

app = Flask(__name__)
app.config.from_envvar('CONFIG_PATH')

extensions.redis.init_app(app)

app.register_blueprint(frontend)
app.register_blueprint(upload, url_prefix='/upload')

if __name__ == "__main__":
    app.debug = True
    app.run()
