# -*- coding: utf-8 -*-

from functools import wraps

from flask import request, abort, g

import models
import extensions


def check_auth(redis, username, password):
    try:
        user = models.User.load(redis, username)
        if user and user.verify_password(password):
            return user
        else:
            return None
    except models.NotFoundException:
        return None


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth:
            abort(401)
        g.user = check_auth(extensions.redis, auth.username, auth.password)
        if not g.user:
            abort(401)
        return f(*args, **kwargs)
    return decorated
