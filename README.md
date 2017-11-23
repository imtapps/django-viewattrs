django-viewattrs
================

This library is how we set permissions at the url / view level

Usage
-----
As of version 1.0.0, Django 1.8+ you must wrap the url list in the `AppyViewAttrs` function.
The old `patterns` method is deprecated.


`

    from viewattrs.urls import url
    
    urlpatterns = apply_view_attrs([
        url('^url-regex', include('myapp.urls'), view_attrs={
            'permissions': ['can_use_app'],
        }),
        url(r'^$', 'example.views.home', name='home', view_attrs={
            'permissions': ['can_view_example'],
        }),
    ])
`

Previous Versions
-----------------
Version 0.0.1 wrapped both patterns and url.

`

    from viewattrs.urls import url, patterns
    
    urlpatterns = patterns(
        '',
        url('^url-regex', include('myapp.urls'), view_attrs={
            'permissions': ['can_use_app'],
        }),
        url(r'^$', 'example.views.home', name='home', view_attrs={
            'permissions': ['can_view_example'],
        }),
    )
`
