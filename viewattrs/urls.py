"""
these functions wrap django's url and patterns functions to allow the
addition of view attributes
"""
from django.conf.urls.defaults import patterns as django_patterns
from django.conf.urls.defaults import url as django_url


def url(regex, view, kwargs=None, name=None, prefix='', view_attrs=None):
    """
    this is a passthrough to Django's url function that also accepts a
    view_attrs keyword argument this allows view_attrs to be attached
    to Django's URL Regex resolver
    """
    url_object = django_url(regex, view, kwargs, name, prefix)
    url_object.view_attrs = view_attrs
    return url_object


def patterns(prefix='', *args):
    """
    this is a passthrough to Django's patterns function that will attach
    any view_atters specified to the callable view objects
    """
    patterns_object = django_patterns(prefix, *args)

    for pattern in patterns_object:
        if getattr(pattern, 'view_attrs', False):
            url_patterns_recurse(pattern, pattern.view_attrs)
    return patterns_object


def url_patterns_recurse(pattern, view_attrs):
    """
    this will handle attaching view_attrs to multiple levels of includes
    in urls.py allowing view_attrs to be specified, and override their
    parent view_attrs
    """
    if hasattr(pattern, 'url_patterns'):
        for ptrn in pattern.url_patterns:
            if getattr(ptrn, 'view_attrs', False):
                new_attrs = view_attrs.copy()
                new_attrs.update(ptrn.view_attrs)
            else:
                new_attrs = view_attrs
            url_patterns_recurse(ptrn, new_attrs)
    else:
        if getattr(pattern, 'callback', False):
            add_view_attrs(pattern.callback, view_attrs)


def add_view_attrs(view, view_attrs):
    """
    add the attributes to the view callable
    """
    for key, value in view_attrs.items():
        setattr(view, key, value)
