# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, abort, current_app, request

import time

import extensions
import models

frontend = Blueprint('frontend', __name__)


@frontend.app_template_filter()
def format_timestamp(value):
    return time.strftime('%B %d, %Y at %H:%M', time.gmtime(value))


@frontend.route("/u/<token>")
def view_upload(token):
    try:
        upload = models.Upload.load(extensions.redis, token)
    except models.NotFoundException:
        abort(404)

    return render_template(
        "upload.html",
        upload=upload,
        url=upload.get_file_url(current_app.config['UPLOAD_URL_BASE'])
    )


@frontend.route('/join', methods=('GET', 'POST'))
def join():
    if request.method == 'POST':
        models.User.create(
            extensions.redis,
            request.form['username'],
            request.form['email'],
            request.form['password']
        )
        return "User Created"
    return render_template('join.html')
