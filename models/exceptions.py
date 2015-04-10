# -*- coding: utf-8 -*-


class NotFoundException(Exception):
    pass


class UserExistsException(Exception):
    pass


class InvalidObjectException(Exception):

    def __init__(self, klass, errors={}):
        Exception.__init__(self)
        self.klass = klass
        self.errors = errors
