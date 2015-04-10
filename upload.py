# -*- coding: utf-8 -*-

from flask import Blueprint, make_response, request, current_app, g, url_for, abort, jsonify

import tinys3

import extensions
import models
import s3
from auth import requires_auth

upload = Blueprint('upload', __name__)


@upload.errorhandler(400)
def http_400(e):
    return make_response("Bad Request", 400)


@upload.errorhandler(401)
def http_401(e):
    response = make_response("Not Authorized", 401)
    response.headers['WWW-Authenticate'] = 'Basic realm="Authentication Required"'
    return response


@upload.errorhandler(403)
def http_403(e):
    return make_response("Forbidden", 403)


@upload.errorhandler(models.NotFoundException)
def models_404(e):
    response = jsonify(error='Not Found')
    response.status_code = 404
    return response

@upload.errorhandler(models.InvalidObjectException)
def validation_400(e):
    response = jsonify(error='Bad Request', errors=e.errors)
    response.status_code = 400
    return response


@upload.route("/sign", methods=('POST',))
@requires_auth
def sign_upload():
    upload = models.Upload.create(
        extensions.redis,
        g.user.username,
        request.form.get('filename'),
        request.form.get('content_type'),
        request.form.get('size')
    )

    policy = upload.generate_upload_policy(current_app.config['S3_BUCKET'])
    policy_string, signature = s3.sign_policy(policy, current_app.config['AWS_SECRET_KEY'])

    return jsonify(
        token=upload.token,
        key=upload.storage_path,
        AWSAccessKeyId=current_app.config['AWS_ACCESS_KEY'],
        acl="public-read",
        success_action_status="200",
        policy=policy_string,
        signature=signature,
        upload_url="https://%s.s3.amazonaws.com" % current_app.config['S3_BUCKET'],
        view_url=url_for("frontend.view_upload", token=upload.token, _external=True),
        direct_url=upload.get_file_url(current_app.config['UPLOAD_URL_BASE'])
    )


@upload.route("/complete", methods=('POST',))
@requires_auth
def complete_upload():
    upload = models.Upload.load(extensions.redis, request.form['token'])
    if not upload:
        abort(404)

    if upload.username != g.user.username:
        abort(404)

    upload.complete(extensions.redis)

    response = jsonify(error=False)
    response.status = "OK"
    response.status_code = 201

    return response


@upload.route("/delete", methods=('POST',))
@requires_auth
def delete_upload():
    upload = models.Upload.load(extensions.redis, request.form['token'])
    if not upload:
        abort(404)

    if upload.username != g.user.username:
        abort(404)

    upload.delete(extensions.redis)

    conn = tinys3.Connection(current_app.config['AWS_ACCESS_KEY'], current_app.config['AWS_SECRET_KEY'])
    conn.delete(upload.storage_path, current_app.config['S3_BUCKET'])

    response = jsonify(error=False)
    response.status_code = 204
    return response
