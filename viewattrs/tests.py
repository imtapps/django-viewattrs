from django.utils import unittest

from django.conf.urls.defaults import url as django_url, include
from viewattrs.urls import url, patterns

class UrlFunctionTests(unittest.TestCase):

    def setUp(self):
        def dummy_view(request):
            pass
        self.dummy_view = dummy_view

        self.args = (r'^dummy/$', self.dummy_view)
        self.kwargs = {'name':"dumbone", 'kwargs':{'number1':123, 'number2':987}, 'prefix':'dumbthree'}

        self.new_kwargs = self.kwargs.copy()
        self.new_kwargs['view_attrs'] = {'one':1, 'two':2}

    def test_behave_like_default_url_function(self):
        "make sure the calling the django url and the overridden url function result in the same object"

        default = django_url(*self.args, **self.kwargs)
        new = url(*self.args, **self.kwargs)

        self.assertEqual(default._callback, new._callback)
        self.assertEqual(default.regex, new.regex)
        self.assertEqual(default.default_args, new.default_args)
        self.assertEqual(default.name, new.name)

    def test_add_view_attrs_to_url_pattern_object(self):
        "make sure that the view_attrs argument to the url pattern object"

        pattern = url(*self.args, **self.new_kwargs)
        self.assertTrue(hasattr(pattern, 'view_attrs'))

    def test_add_attributes_to_callable(self):
        "make sure the that view_attrs are added to the callable as attributes"

        patterns('', url(*self.args, **self.new_kwargs))

        self.assertEqual(self.dummy_view.one, 1)
        self.assertEqual(self.dummy_view.two, 2)

    def test_inherit_parent_attributes(self):
        "make sure that the include's attributes will propogate to children callables"
        def another_func(request):
            pass
        child_patterns = patterns('',
            url(*self.args, **self.kwargs),
            url('asdf', another_func, **self.kwargs)
        )

        patterns('',
            url('^xxx$', include(child_patterns), view_attrs={'asdf':1234, 'wxyz':'abcd'})
        )

        self.assertEqual(self.dummy_view.asdf, 1234)
        self.assertEqual(self.dummy_view.wxyz, 'abcd')
        self.assertEqual(another_func.asdf, 1234)
        self.assertEqual(another_func.wxyz, 'abcd')

    def test_inherit_multiple_levels_deep(self):
        "make sure that the inheritence follows multiple levels deep"
        great_grandchild_patterns = patterns('',
            url(*self.args, **self.kwargs),
        )
        grandchild_patterns = patterns('',
            url('^xxx$', include(great_grandchild_patterns), view_attrs={'level_three':'three'})
        )
        child_patterns = patterns('',
            url('^xxx$', include(grandchild_patterns), view_attrs={'level_two':'two',})
        )
        patterns('',
            url('^xxx$', include(child_patterns), view_attrs={'level_one':'one',})
        )

        self.assertEqual(self.dummy_view.level_one, 'one')
        self.assertEqual(self.dummy_view.level_two, 'two')
        self.assertEqual(self.dummy_view.level_three, 'three')

    def test_override_parents_at_child_levels(self):
        "make sure that the children override the parents"
        kwargs = self.kwargs.copy()
        kwargs['view_attrs'] = {'four':4444}
        great_grandchild_patterns = patterns('',
            url(*self.args, **kwargs),
        )
        grandchild_patterns = patterns('',
            url('^xxx$', include(great_grandchild_patterns), view_attrs={'three':333,'four':444})
        )
        child_patterns = patterns('',
            url('^xxx$', include(grandchild_patterns), view_attrs={'two':22, 'three':33,'four':44})
        )
        patterns('',
            url('^xxx$', include(child_patterns), view_attrs={'one':1, 'two':2, 'three':3, 'four':4})
        )

        self.assertEqual(self.dummy_view.one, 1)
        self.assertEqual(self.dummy_view.two, 22)
        self.assertEqual(self.dummy_view.three, 333)
        self.assertEqual(self.dummy_view.four, 4444)

    def test_remain_unaffected_if_not_nested_under_first_level(self):
        "make sure that a callable doesn't get attributes when it shouldn't"
        def other_dummy(request):
            pass
        kwargs = self.kwargs.copy()
        kwargs['view_attrs'] = {'four':4444}
        great_grandchild_patterns = patterns('',
            url(*self.args, **kwargs),
        )
        other_great_grandchild_patterns = patterns('',
            url('asdf', other_dummy, **self.kwargs),
        )
        other_grandchild_patterns = patterns('',
            url('^xxx$', include(other_great_grandchild_patterns))
        )
        grandchild_patterns = patterns('',
            url('^xxx$', include(great_grandchild_patterns), view_attrs={'three':333,'four':444})
        )
        child_patterns = patterns('',
            url('^xxx$', include(grandchild_patterns), view_attrs={'two':22, 'three':33,'four':44})
        )
        other_child_patterns = patterns('',
            url('^xxx$', include(other_grandchild_patterns))
        )
        patterns('',
            url('^xxx$', include(child_patterns), view_attrs={'one':1, 'two':2, 'three':3, 'four':4}),
            url('^xxx$', include(other_child_patterns))
        )

        self.assertFalse(hasattr(other_dummy, 'one'))
        self.assertFalse(hasattr(other_dummy, 'two'))
        self.assertFalse(hasattr(other_dummy, 'three'))
        self.assertFalse(hasattr(other_dummy, 'four'))
        self.assertEqual(self.dummy_view.one, 1)
        self.assertEqual(self.dummy_view.two, 22)
        self.assertEqual(self.dummy_view.three, 333)
        self.assertEqual(self.dummy_view.four, 4444)

    def test_only_get_first_level_if_only_nested_under_first_level(self):
        "make sure that a callable gets the attributes that it inherits from its 1 parent"
        def other_dummy(request):
            pass
        kwargs = self.kwargs.copy()
        kwargs['view_attrs'] = {'four':4444}
        great_grandchild_patterns = patterns('',
            url(*self.args, **kwargs),
        )
        other_great_grandchild_patterns = patterns('',
            url('asdf', other_dummy, **self.kwargs),
        )
        other_grandchild_patterns = patterns('',
            url('^xxx$', include(other_great_grandchild_patterns))
        )
        grandchild_patterns = patterns('',
            url('^xxx$', include(great_grandchild_patterns), view_attrs={'three':333,'four':444})
        )
        other_child_patterns = patterns('',
            url('^xxx$', include(other_grandchild_patterns))
        )
        child_patterns = patterns('',
            url('^xxx$', include(grandchild_patterns), view_attrs={'two':22, 'three':33,'four':44}),
            url('^xxx$', include(other_child_patterns))
        )
        patterns('',
            url('^xxx$', include(child_patterns), view_attrs={'one':1, 'two':2, 'three':3, 'four':4}),

        )

        self.assertEqual(other_dummy.one, 1)
        self.assertEqual(other_dummy.two, 2)
        self.assertEqual(other_dummy.three, 3)
        self.assertEqual(other_dummy.four, 4)
        self.assertEqual(self.dummy_view.one, 1)
        self.assertEqual(self.dummy_view.two, 22)
        self.assertEqual(self.dummy_view.three, 333)
        self.assertEqual(self.dummy_view.four, 4444)

    def test_get_first_and_second_level_if_nested_under_second(self):
        "make sure that a callable gets the attributes that it inherits from its 2 parents"
        def other_dummy(request):
            pass
        kwargs = self.kwargs.copy()
        kwargs['view_attrs'] = {'four':4444}
        great_grandchild_patterns = patterns('',
            url(*self.args, **kwargs),
        )
        other_great_grandchild_patterns = patterns('',
            url('asdf', other_dummy, **self.kwargs),
        )
        other_grandchild_patterns = patterns('',
            url('^xxx$', include(other_great_grandchild_patterns))
        )
        other_child_patterns = patterns('',
            url('^xxx$', include(other_grandchild_patterns))
        )
        grandchild_patterns = patterns('',
            url('^xxx$', include(great_grandchild_patterns), view_attrs={'three':333,'four':444}),
            url('^xxx$', include(other_child_patterns))
        )
        child_patterns = patterns('',
            url('^xxx$', include(grandchild_patterns), view_attrs={'two':22, 'three':33,'four':44}),
        )
        patterns('',
            url('^xxx$', include(child_patterns), view_attrs={'one':1, 'two':2, 'three':3, 'four':4}),

        )

        self.assertEqual(other_dummy.one, 1)
        self.assertEqual(other_dummy.two, 22)
        self.assertEqual(other_dummy.three, 33)
        self.assertEqual(other_dummy.four, 44)
        self.assertEqual(self.dummy_view.one, 1)
        self.assertEqual(self.dummy_view.two, 22)
        self.assertEqual(self.dummy_view.three, 333)
        self.assertEqual(self.dummy_view.four, 4444)

    def test_get_first_and_second_and_third_level_if_nested_under_third(self):
        "make sure that a callable gets the attributes that it inherits from its 3 parents"
        def other_dummy(request):
            pass
        kwargs = self.kwargs.copy()
        kwargs['view_attrs'] = {'four':4444}
        other_great_grandchild_patterns = patterns('',
            url('asdf', other_dummy, **self.kwargs),
        )
        other_grandchild_patterns = patterns('',
            url('^xxx$', include(other_great_grandchild_patterns))
        )
        other_child_patterns = patterns('',
            url('^xxx$', include(other_grandchild_patterns))
        )
        great_grandchild_patterns = patterns('',
            url(*self.args, **kwargs),
            url('^xxx$', include(other_child_patterns))
        )
        grandchild_patterns = patterns('',
            url('^xxx$', include(great_grandchild_patterns), view_attrs={'three':333,'four':444}),
        )
        child_patterns = patterns('',
            url('^xxx$', include(grandchild_patterns), view_attrs={'two':22, 'three':33,'four':44}),
        )
        patterns('',
            url('^xxx$', include(child_patterns), view_attrs={'one':1, 'two':2, 'three':3, 'four':4}),

        )

        self.assertEqual(other_dummy.one, 1)
        self.assertEqual(other_dummy.two, 22)
        self.assertEqual(other_dummy.three, 333)
        self.assertEqual(other_dummy.four, 444)
        self.assertEqual(self.dummy_view.one, 1)
        self.assertEqual(self.dummy_view.two, 22)
        self.assertEqual(self.dummy_view.three, 333)
        self.assertEqual(self.dummy_view.four, 4444)