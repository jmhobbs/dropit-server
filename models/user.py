# -*- coding: utf-8 -*-

import time
from passlib.hash import bcrypt
from .exceptions import NotFoundException, UserExistsException, InvalidObjectException


class User(object):

    def __init__(self):
        self.username = None
        self._password = None
        self.email = None
        self.created = 0

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, new_password):
        self._password = bcrypt.encrypt(new_password)

    def verify_password(self, password):
        return bcrypt.verify(password, self._password)

    def hash_key(self):
        return "user:%s" % self.username

    @classmethod
    def create(klass, redis, username, email, new_password):
        user = klass()
        user.username = username
        user.email = email
        user.password = new_password
        user.created = time.time()

        if redis.exists(user.hash_key()):
            raise UserExistsException

        user.store(redis)
        return user

    @classmethod
    def load(klass, redis, username):
        user = klass()
        user.username = username

        result = redis.hgetall(user.hash_key())
        if not result:
            raise NotFoundException('User Not Found')

        user._password = result['password']
        user.email = result['email']
        user.created = float(result['created'])

        return user

    def validate(self):
        errors = {}

        if not self._password:
            errors['password'] = 'Password is required.'

        if not self.email:
            errors['email'] = 'Email is required.'

        if not self.username:
            errors['username'] = 'Username is required.'

        if errors:
            raise InvalidObjectException(self.__class__, errors)


    def store(self, redis):
        self.validate()

        redis.hmset(self.hash_key(), {
            "password": self._password,
            "email": self.email,
            "created": self.created
        })
        redis.set("email:%s" % self.email, self.username)
