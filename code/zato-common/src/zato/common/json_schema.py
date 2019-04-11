# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os
from json import loads
from logging import getLogger

# JSON Schema
from jsonschema import validate as js_validate
from jsonschema.exceptions import ValidationError as JSValidationError
from jsonschema.validators import validator_for

# Zato
from zato.common import CHANNEL
from zato.common.json_rpc import ErrorCtx, JSONRPCBadRequest, ItemResponse

# ################################################################################################################################

# Type checking
import typing

if typing.TYPE_CHECKING:

    # stdlib
    from typing import Callable

    # Bunch
    from bunch import Bunch

    # For pyflakes
    Bunch = Bunch
    Callable = Callable

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ValidationException(Exception):
    pass

# ################################################################################################################################
# ################################################################################################################################

class ValidationError(object):
    """ Base class for validation error-related classes.
    """
    __slots__ = 'cid', 'error_msg', 'error_extra'

    def __init__(self, cid, error_msg, error_extra=None):
        # type: (unicode, unicode, dict)
        self.cid = cid
        self.error_msg = error_msg
        self.error_extra = error_extra

    def get_error_message(self):
        # type: () -> unicode

        out = 'Invalid request'
        if self.error_msg:
            out += '; {}'.format(self.error_msg)

        return out

    def serialize(self):
        raise NotImplementedError('Must be overridden in subclasses')

# ################################################################################################################################
# ################################################################################################################################

class DictError(ValidationError):
    """ An error reporter that serializes JSON Schema validation errors into Python dict responses.
    """
    def serialize(self):
        # type: () -> dict
        return {
            'is_ok': False,
            'cid': self.cid,
            'message': self.get_error_message()
        }

# ################################################################################################################################
# ################################################################################################################################

class JSONRPCError(ValidationError):
    """ An error reporter that serializes JSON Schema validation errors into JSON-RPC responses.
    """
    def serialize(self):
        # type: () -> dict

        error_ctx = ErrorCtx()
        error_ctx.cid = self.cid

        error_ctx.code = JSONRPCBadRequest.code
        error_ctx.message = 'Invalid request'

        # This may be optionally turned off
        error_ctx.message = self.get_error_message()

        out = ItemResponse()
        out.id = self.error_extra['json_rpc_id']
        out.error = error_ctx

        return out.to_dict()

# ################################################################################################################################

channel_type_to_error_class = {
    CHANNEL.HTTP_SOAP: DictError,
    CHANNEL.JSON_RPC: JSONRPCError,
    CHANNEL.SERVICE: DictError,
}

# ################################################################################################################################
# ################################################################################################################################

class ValidationConfig(object):
    """ An individual set of configuration options - each object requiring validation (e.g. each channel)
    will have its own instance of this class assigned to its validator.
    """
    __slots__ = 'is_enabled', 'object_type', 'object_name', 'schema_path', 'schema', 'validator', 'needs_err_details'

    def __init__(self):
        self.is_enabled = None   # type: bool

        # Object type is channel type or, in the future, one of outgoing connections
        # whose requests to external resources we may also want to validate.
        self.object_type = None # type: unicode

        self.object_name = None # type: unicode
        self.schema_path = None # type: unicode
        self.schema = None      # type: dict
        self.validator = None   # type: object
        self.needs_err_details = None # type: bool

# ################################################################################################################################
# ################################################################################################################################

class Result(object):
    __slots__ = 'is_ok', 'cid', 'error_msg', 'error_extra', 'object_type'

    def __init__(self):
        self.is_ok = None        # type: bool
        self.cid = None          # type: unicode
        self.error_msg = None    # type: unicode
        self.error_extra = None  # type: dict
        self.object_type = None  # type: unicode

    def __bool__(self):
        return bool(self.is_ok)

    __nonzero__ = __bool__

    def get_error(self):
        # type: () -> dict
        ErrorClass = channel_type_to_error_class[self.object_type]
        error = ErrorClass(self.cid, self.error_msg, self.error_extra) # type: ValidationError
        return error.serialize()

# ################################################################################################################################
# ################################################################################################################################

class Validator(object):
    """ Validates JSON requests against a previously assigned schema and serializes errors according to the caller's type,
    e.g. using REST or JSON-RPC.
    """
    __slots__ = 'is_initialized', 'config'

    def __init__(self):
        self.is_initialized = False # type: bool
        self.config = None # type: ValidationConfig

    def init(self):
        if not os.path.exists(self.config.schema_path):
            raise ValidationException('JSON schema not found `{}` ({})'.format(self.config.schema_path))

        # The file is sure to exist
        with open(self.config.schema_path) as f:
            schema = f.read()

        # Parse the contents as JSON
        schema = loads(schema)

        # Assign the schema and validator for the schema for later use
        self.config.schema = schema
        self.config.validator = validator_for(schema)

        # Everything is set up = we are initialized
        self.is_initialized = True

    def validate(self, cid, data, object_type=None, object_name=None, needs_err_details=None, _validate=js_validate):
        # type: (object, Callable) -> Result

        # Result we will return
        result = Result()
        result.cid = cid

        object_type = object_type or self.config.object_type
        object_name or self.config.object_name
        needs_err_details or self.config.needs_err_details

        try:
            js_validate(data, self.config.schema, self.config.validator)
        except JSValidationError as e:

            # These will be always used, no matter the object/channel type
            result.is_ok = False
            result.object_type = object_type

            # This is optional because details of errors will not be always desirable to be returne
            if needs_err_details:
                result.error_msg = str(e)

            # This is applicable only to JSON-RPC
            if object_type == CHANNEL.JSON_RPC:
                result.error_extra = {'json_rpc_id': data.get('id')}
        else:
            result.is_ok = True

        return result

# ################################################################################################################################
# ################################################################################################################################
