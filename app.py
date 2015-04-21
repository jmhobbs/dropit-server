# -*- coding: utf-8 -*-

from flask import Flask

import extensions

from frontend import frontend
from api import api

app = Flask(__name__)
app.config.from_envvar('CONFIG_PATH')

extensions.redis.init_app(app)

app.register_blueprint(frontend)
app.register_blueprint(api, url_prefix='/api')

if __name__ == "__main__":
    app.debug = True
    app.run()
