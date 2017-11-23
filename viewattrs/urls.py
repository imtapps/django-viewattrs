#
# Wraps django's url function to allow the addition of view attributes
#
from django.conf.urls import url as django_url


def url(regex, view, kwargs=None, name=None, view_attrs=None):
    """
    this is a passthrough to Django's url function that also accepts a
    view_attrs keyword argument this allows view_attrs to be attached
    to Django's URL Regex resolver
    """
    url_object = django_url(regex, view, kwargs, name)
    url_object.view_attrs = view_attrs
    return url_object


def apply_view_attrs(urls_list):
    """
    If a view has view attrs, make sure it applies to all its children
    if we're working with an includes. This allows you to set a view attribute
    at a top level `include` without needing to apply it to every single view.
    """
    for url_item in urls_list:
        if getattr(url_item, 'view_attrs', False):
            _urls_list_recurse(url_item, url_item.view_attrs)
    return urls_list


def _urls_list_recurse(url_item, view_attrs):
    """
    this will handle attaching view_attrs to multiple levels of includes
    in urls.py allowing view_attrs to be specified, and override their
    parent view_attrs
    """
    if hasattr(url_item, 'url_patterns'):
        for ptrn in url_item.url_patterns:
            if getattr(ptrn, 'view_attrs', False):
                new_attrs = view_attrs.copy()
                new_attrs.update(ptrn.view_attrs)
            else:
                new_attrs = view_attrs
            _urls_list_recurse(ptrn, new_attrs)
    else:
        if getattr(url_item, 'callback', False):
            _add_view_attrs(url_item.callback, view_attrs)


def _add_view_attrs(view, view_attrs):
    """
    add the attributes to the view callable
    """
    for key, value in view_attrs.items():
        setattr(view, key, value)
