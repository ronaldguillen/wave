"""
The most important decorator in this module is `@api_view`, which is used
for writing function-based views with REST framework.

There are also various decorators for setting the API policies on function
based views, as well as the `@detail_route` and `@list_route` decorators, which are
used to annotate methods on viewsets that should be included by routers.
"""
from __future__ import unicode_literals

import types

from django.utils import six

from wave.views import RestView


def rest_verbs(http_method_names=None):

    """
    Decorator that converts a function-based view into an RestView subclass.
    Takes a list of allowed methods for the view as an argument.
    """
    http_method_names = ['GET'] if (http_method_names is None) else http_method_names

    def decorator(func):

        WrappedRestView = type(
            six.PY3 and 'WrappedRestView' or b'WrappedRestView',
            (RestView,),
            {'__doc__': func.__doc__}
        )

        # Note, the above allows us to set the docstring.
        # It is the equivalent of:
        #
        #     class WrappedRestView(RestView):
        #         pass
        #     WrappedRestView.__doc__ = func.doc    <--- Not possible to do this

        # api_view applied without (method_names)
        assert not(isinstance(http_method_names, types.FunctionType)), \
            '@api_view missing list of allowed HTTP methods'

        # api_view applied with eg. string instead of list of strings
        assert isinstance(http_method_names, (list, tuple)), \
            '@api_view expected a list of strings, received %s' % type(http_method_names).__name__

        allowed_methods = set(http_method_names) | set(('options',))
        WrappedRestView.http_method_names = [method.lower() for method in allowed_methods]

        def handler(self, *args, **kwargs):
            return func(*args, **kwargs)

        for method in http_method_names:
            setattr(WrappedRestView, method.lower(), handler)

        WrappedRestView.__name__ = func.__name__

        WrappedRestView.renderer_classes = getattr(func, 'renderer_classes',
                                                  RestView.renderer_classes)

        WrappedRestView.parser_classes = getattr(func, 'parser_classes',
                                                RestView.parser_classes)

        WrappedRestView.authentication_classes = getattr(func, 'authentication_classes',
                                                        RestView.authentication_classes)

        WrappedRestView.throttle_classes = getattr(func, 'throttle_classes',
                                                  RestView.throttle_classes)

        WrappedRestView.permission_classes = getattr(func, 'permission_classes',
                                                    RestView.permission_classes)

        return WrappedRestView.as_view()
    return decorator


def renderer_classes(renderer_classes):
    def decorator(func):
        func.renderer_classes = renderer_classes
        return func
    return decorator


def parser_classes(parser_classes):
    def decorator(func):
        func.parser_classes = parser_classes
        return func
    return decorator


def authentication_classes(authentication_classes):
    def decorator(func):
        func.authentication_classes = authentication_classes
        return func
    return decorator


def throttle_classes(throttle_classes):
    def decorator(func):
        func.throttle_classes = throttle_classes
        return func
    return decorator


def permission_classes(permission_classes):
    def decorator(func):
        func.permission_classes = permission_classes
        return func
    return decorator


def detail_route(methods=None, **kwargs):
    """
    Used to mark a method on a ViewSet that should be routed for detail requests.
    """
    methods = ['get'] if (methods is None) else methods

    def decorator(func):
        func.bind_to_methods = methods
        func.detail = True
        func.kwargs = kwargs
        return func
    return decorator


def list_route(methods=None, **kwargs):
    """
    Used to mark a method on a ViewSet that should be routed for list requests.
    """
    methods = ['get'] if (methods is None) else methods

    def decorator(func):
        func.bind_to_methods = methods
        func.detail = False
        func.kwargs = kwargs
        return func
    return decorator
