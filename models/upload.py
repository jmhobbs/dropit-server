# -*- coding: utf-8 -*-

import base64
import time
import datetime
import os
from .exceptions import NotFoundException, InvalidObjectException


def _generate_token(redis):
    '''
    Takes a monotonically incrementing counter and adds some noise so
    you can't easily guess valid keys.
    '''
    token_base = redis.incr("token")
    return base64.urlsafe_b64encode(str(token_base) + str(os.urandom(4))).rstrip('=')


class Upload(object):

    def __init__(self):
        object.__init__(self)
        self.username = None
        self.filename = None
        self.content_type = 'application/octet-stream'
        self.token = None
        self.size = 0
        self.created = 0
        self.uploaded = 0

    @classmethod
    def create(klass, redis, username, filename, content_type, size):
        upload = klass()
        upload.username = username
        upload.filename = filename
        upload.token = _generate_token(redis)
        upload.content_type = content_type
        upload.size = size
        upload.created = time.time()
        upload.store(redis)
        return upload

    @property
    def storage_path(self):
        return u"%s/%s/%s" % (self.username, self.token, self.filename)

    def hash_key(self):
        return "upload:%s" % self.token

    @classmethod
    def load(klass, redis, token):
        upload = klass()
        upload.token = token

        result = redis.hgetall(upload.hash_key())
        if not result:
            raise NotFoundException('Upload Not Found')

        upload.username = result['username']
        upload.filename = result['filename']
        upload.content_type = result['content-type']
        upload.size = int(result['size'])
        upload.created = float(result['created'])
        upload.uploaded = float(result['uploaded'])

        return upload

    def complete(self, redis):
        redis.hset(self.hash_key(), "uploaded", time.time())

    def delete(self, redis):
        redis.lrem("uploads", 0, self.token)
        redis.lrem("uploads:%s" % self.username, 0, self.token)
        redis.delete(self.hash_key())

    def validate(self):
        errors = {}

        required = ('username', 'filename', 'content_type', 'size')
        for field in required:
            if not getattr(self, field):
                errors[field] = "%s is required" % field

        if errors:
            raise InvalidObjectException(self.__class__, errors)

    def store(self, redis):
        self.validate()

        redis.hmset(self.hash_key(), {
            "username": self.username,
            "filename": self.filename,
            "content-type": self.content_type,
            "size": self.size,
            "created": self.created,
            "uploaded": self.uploaded
        })

        redis.lpush("uploads", self.token)
        redis.lpush("uploads:%s" % self.username, self.token)

    def generate_upload_policy(self, bucket_name, minutes_valid=5, max_bytes=104857600):
        expiration = datetime.datetime.utcnow() + datetime.timedelta(minutes=minutes_valid)

        return {
            "expiration": expiration.strftime('%Y-%m-%dT%H:%M:%SZ'),
            "conditions": [
                {"bucket": bucket_name},
                {"acl": "public-read"},
                ["eq", "$key", self.storage_path],
                {"content-type": self.content_type},
                ["content-length-range", 0, max_bytes],
                {'success_action_status': '200'}
                ]
            }

    @property
    def is_uploaded(self):
        return self.uploaded > 0

    @property
    def is_image(self):
        return self.content_type[:6] == 'image/'

    def get_file_url(self, url_base):
        return url_base + self.storage_path
