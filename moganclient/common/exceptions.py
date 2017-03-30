#   Copyright 2016 Huawei, Inc. All rights reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

import inspect
import sys

from oslo_serialization import jsonutils
import six

from moganclient.common.i18n import _


class ClientException(Exception):
    """The base exception class for all exceptions this library raises."""
    def __init__(self, message=None):
        self.message = message

    def __str__(self):
        return self.message or self.__class__.__doc__


class ValidationError(ClientException):
    """Error in validation on API client side."""
    pass


class UnsupportedVersion(ClientException):
    """User is trying to use an unsupported version of the API."""
    pass


class CommandError(ClientException):
    """Error in CLI tool."""
    pass


class AuthorizationFailure(ClientException):
    """Cannot authorize API client."""
    pass


class ConnectionError(ClientException):
    """Cannot connect to API service."""
    pass


class ConnectionRefused(ConnectionError):
    """Connection refused while trying to connect to API service."""
    pass


class AuthPluginOptionsMissing(AuthorizationFailure):
    """Auth plugin misses some options."""
    def __init__(self, opt_names):
        super(AuthPluginOptionsMissing, self).__init__(
            _("Authentication failed. Missing options: %s") %
            ", ".join(opt_names))
        self.opt_names = opt_names


class AuthSystemNotFound(AuthorizationFailure):
    """User has specified an AuthSystem that is not installed."""
    def __init__(self, auth_system):
        super(AuthSystemNotFound, self).__init__(
            _("AuthSystemNotFound: %r") % auth_system)
        self.auth_system = auth_system


class NoUniqueMatch(ClientException):
    """Multiple entities found instead of one."""
    pass


class EndpointException(ClientException):
    """Something is rotten in Service Catalog."""
    pass


class EndpointNotFound(EndpointException):
    """Could not find requested endpoint in Service Catalog."""
    pass


class AmbiguousEndpoints(EndpointException):
    """Found more than one matching endpoint in Service Catalog."""
    def __init__(self, endpoints=None):
        super(AmbiguousEndpoints, self).__init__(
            _("AmbiguousEndpoints: %r") % endpoints)
        self.endpoints = endpoints


class HttpError(ClientException):
    """The base exception class for all HTTP exceptions."""
    status_code = 0
    message = _("HTTP Error")

    def __init__(self, message=None, details=None,
                 response=None, request_id=None,
                 url=None, method=None, status_code=None):
        self.status_code = status_code or self.status_code
        self.message = message or self.message
        self.details = details
        self.request_id = request_id
        self.response = response
        self.url = url
        self.method = method
        formatted_string = "%s (HTTP %s)" % (self.message, self.status_code)
        if request_id:
            formatted_string += " (Request-ID: %s)" % request_id
        super(HttpError, self).__init__(formatted_string)


class HTTPRedirection(HttpError):
    """HTTP Redirection."""
    message = _("HTTP Redirection")


class HTTPClientError(HttpError):
    """Client-side HTTP error.

    Exception for cases in which the client seems to have erred.
    """
    message = _("HTTP Client Error")


class HttpServerError(HttpError):
    """Server-side HTTP error.

    Exception for cases in which the server is aware that it has
    erred or is incapable of performing the request.
    """
    message = _("HTTP Server Error")


class MultipleChoices(HTTPRedirection):
    """HTTP 300 - Multiple Choices.

    Indicates multiple options for the resource that the client may follow.
    """

    status_code = 300
    message = _("Multiple Choices")


class BadRequest(HTTPClientError):
    """HTTP 400 - Bad Request.

    The request cannot be fulfilled due to bad syntax.
    """
    status_code = 400
    message = _("Bad Request")


class Unauthorized(HTTPClientError):
    """HTTP 401 - Unauthorized.

    Similar to 403 Forbidden, but specifically for use when authentication
    is required and has failed or has not yet been provided.
    """
    status_code = 401
    message = _("Unauthorized")


class PaymentRequired(HTTPClientError):
    """HTTP 402 - Payment Required.

    Reserved for future use.
    """
    status_code = 402
    message = _("Payment Required")


class Forbidden(HTTPClientError):
    """HTTP 403 - Forbidden.

    The request was a valid request, but the server is refusing to respond
    to it.
    """
    status_code = 403
    message = _("Forbidden")


class NotFound(HTTPClientError):
    """HTTP 404 - Not Found.

    The requested resource could not be found but may be available again
    in the future.
    """
    status_code = 404
    message = _("Not Found")


class MethodNotAllowed(HTTPClientError):
    """HTTP 405 - Method Not Allowed.

    A request was made of a resource using a request method not supported
    by that resource.
    """
    status_code = 405
    message = _("Method Not Allowed")


class NotAcceptable(HTTPClientError):
    """HTTP 406 - Not Acceptable.

    The requested resource is only capable of generating content not
    acceptable according to the Accept headers sent in the request.
    """
    status_code = 406
    message = _("Not Acceptable")


class ProxyAuthenticationRequired(HTTPClientError):
    """HTTP 407 - Proxy Authentication Required.

    The client must first authenticate itself with the proxy.
    """
    status_code = 407
    message = _("Proxy Authentication Required")


class RequestTimeout(HTTPClientError):
    """HTTP 408 - Request Timeout.

    The server timed out waiting for the request.
    """
    status_code = 408
    message = _("Request Timeout")


class Conflict(HTTPClientError):
    """HTTP 409 - Conflict.

    Indicates that the request could not be processed because of conflict
    in the request, such as an edit conflict.
    """
    status_code = 409
    message = _("Conflict")


class Gone(HTTPClientError):
    """HTTP 410 - Gone.

    Indicates that the resource requested is no longer available and will
    not be available again.
    """
    status_code = 410
    message = _("Gone")


class LengthRequired(HTTPClientError):
    """HTTP 411 - Length Required.

    The request did not specify the length of its content, which is
    required by the requested resource.
    """
    status_code = 411
    message = _("Length Required")


class PreconditionFailed(HTTPClientError):
    """HTTP 412 - Precondition Failed.

    The server does not meet one of the preconditions that the requester
    put on the request.
    """
    status_code = 412
    message = _("Precondition Failed")


class RequestEntityTooLarge(HTTPClientError):
    """HTTP 413 - Request Entity Too Large.

    The request is larger than the server is willing or able to process.
    """
    status_code = 413
    message = _("Request Entity Too Large")

    def __init__(self, *args, **kwargs):
        try:
            self.retry_after = int(kwargs.pop('retry_after'))
        except (KeyError, ValueError):
            self.retry_after = 0

        super(RequestEntityTooLarge, self).__init__(*args, **kwargs)


class RequestUriTooLong(HTTPClientError):
    """HTTP 414 - Request-URI Too Long.

    The URI provided was too long for the server to process.
    """
    status_code = 414
    message = _("Request-URI Too Long")


class UnsupportedMediaType(HTTPClientError):
    """HTTP 415 - Unsupported Media Type.

    The request entity has a media type which the server or resource does
    not support.
    """
    status_code = 415
    message = _("Unsupported Media Type")


class RequestedRangeNotSatisfiable(HTTPClientError):
    """HTTP 416 - Requested Range Not Satisfiable.

    The client has asked for a portion of the file, but the server cannot
    supply that portion.
    """
    status_code = 416
    message = _("Requested Range Not Satisfiable")


class ExpectationFailed(HTTPClientError):
    """HTTP 417 - Expectation Failed.

    The server cannot meet the requirements of the Expect request-header field.
    """
    status_code = 417
    message = _("Expectation Failed")


class UnprocessableEntity(HTTPClientError):
    """HTTP 422 - Unprocessable Entity.

    The request was well-formed but was unable to be followed due to semantic
    errors.
    """
    status_code = 422
    message = _("Unprocessable Entity")


class InternalServerError(HttpServerError):
    """HTTP 500 - Internal Server Error.

    A generic error message, given when no more specific message is suitable.
    """
    status_code = 500
    message = _("Internal Server Error")


# NotImplemented is a python keyword.
class HttpNotImplemented(HttpServerError):
    """HTTP 501 - Not Implemented.

    The server either does not recognize the request method, or it lacks
    the ability to fulfill the request.
    """
    status_code = 501
    message = _("Not Implemented")


class BadGateway(HttpServerError):
    """HTTP 502 - Bad Gateway.

    The server was acting as a gateway or proxy and received an invalid
    response from the upstream server.
    """
    status_code = 502
    message = _("Bad Gateway")


class ServiceUnavailable(HttpServerError):
    """HTTP 503 - Service Unavailable.

    The server is currently unavailable.
    """
    status_code = 503
    message = _("Service Unavailable")


class GatewayTimeout(HttpServerError):
    """HTTP 504 - Gateway Timeout.

    The server was acting as a gateway or proxy and did not receive a timely
    response from the upstream server.
    """
    status_code = 504
    message = _("Gateway Timeout")


class HttpVersionNotSupported(HttpServerError):
    """HTTP 505 - HttpVersion Not Supported.

    The server does not support the HTTP protocol version used in the request.
    """
    status_code = 505
    message = _("HTTP Version Not Supported")


# _code_map contains all the classes that have status_code attribute.
_code_map = dict(
    (getattr(obj, 'status_code', None), obj)
    for name, obj in vars(sys.modules[__name__]).items()
    if inspect.isclass(obj) and getattr(obj, 'status_code', False)
)


def from_response(response, method, url):
    """Returns an instance of :class:`HttpError` or subclass based on response.

    :param response: instance of `requests.Response` class
    :param method: HTTP method used for request
    :param url: URL used for request
    """

    # NOTE(liusheng): for pecan's response, the request_id is
    # "Openstack-Request-Id"
    req_id = (response.headers.get("x-openstack-request-id") or
              response.headers.get("Openstack-Request-Id"))
    kwargs = {
        "status_code": response.status_code,
        "response": response,
        "method": method,
        "url": url,
        "request_id": req_id,
    }
    if "retry-after" in response.headers:
        kwargs["retry_after"] = response.headers["retry-after"]

    content_type = response.headers.get("Content-Type", "")
    if content_type.startswith("application/json"):
        try:
            body = response.json()
        except ValueError:
            pass
        else:
            if hasattr(body, 'keys'):
                # NOTE(RuiChen): WebOb<1.6.0 will return a nested dict
                # structure where the error keys to the message/details/code.
                # WebOb>=1.6.0 returns just a response body as a single dict,
                # not nested, so we have to handle both cases (since we can't
                # trust what we're given with content_type: application/json
                # either way.
                if 'message' in body:
                    # WebOb>=1.6.0 case
                    error = body
                else:
                    # WebOb<1.6.0 where we assume there is a single error
                    # message key to the body that has the message and details.
                    error = body.get(list(body)[0])
                    # NOTE(liusheng): the response.json() may like this:
                    # {u'error_message': u'{"debuginfo": null, "faultcode":
                    # "Client", "faultstring": "error message"}'}, the
                    # "error_message" in the body is also a json string.
                    if isinstance(error, six.string_types):
                        error = jsonutils.loads(error)

                if hasattr(error, 'keys'):
                    kwargs['message'] = (error.get('message') or
                                         error.get('faultstring'))
                    kwargs['details'] = (error.get('details') or
                                         six.text_type(body))
    elif content_type.startswith("text/"):
        kwargs["details"] = getattr(response, 'text', '')

    try:
        cls = _code_map[response.status_code]
    except KeyError:
        if 500 <= response.status_code < 600:
            cls = HttpServerError
        elif 400 <= response.status_code < 500:
            cls = HTTPClientError
        else:
            cls = HttpError
    return cls(**kwargs)
