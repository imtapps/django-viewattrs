from django import test
from django.conf.urls import url as django_url, include
from viewattrs.urls import url, apply_view_attrs


class UrlFunctionTests(test.TestCase):

    def setUp(self):

        def dummy_view(request):
            pass

        self.dummy_view = dummy_view

        self.args = (r'^dummy/$', self.dummy_view)
        self.kwargs = {'name': "dumbone", 'kwargs': {'number1': 123, 'number2': 987}}

        self.new_kwargs = self.kwargs.copy()
        self.new_kwargs['view_attrs'] = {'one': 1, 'two': 2}

    def test_behave_like_default_url_function(self):
        default = django_url(*self.args, **self.kwargs)
        new = url(*self.args, **self.kwargs)

        self.assertEqual(default.callback, new.callback)
        self.assertEqual(default.regex, new.regex)
        self.assertEqual(default.default_args, new.default_args)
        self.assertEqual(default.name, new.name)

    def test_add_view_attrs_to_url_pattern_object(self):
        pattern = url(*self.args, **self.new_kwargs)
        self.assertTrue(hasattr(pattern, 'view_attrs'))

    def test_add_attributes_to_callable(self):
        apply_view_attrs([url(*self.args, **self.new_kwargs)])

        self.assertEqual(self.dummy_view.one, 1)
        self.assertEqual(self.dummy_view.two, 2)

    def test_inherit_parent_attributes(self):

        def another_func(request):
            pass

        patterns_1 = apply_view_attrs([url(*self.args, **self.kwargs), url('asdf', another_func, **self.kwargs)])
        apply_view_attrs([url('^xxx$', include(patterns_1), view_attrs={'asdf': 1234, 'wxyz': 'abcd'})])

        self.assertEqual(self.dummy_view.asdf, 1234)
        self.assertEqual(self.dummy_view.wxyz, 'abcd')
        self.assertEqual(another_func.asdf, 1234)
        self.assertEqual(another_func.wxyz, 'abcd')

    def test_inherit_multiple_levels_deep(self):
        patterns_3 = apply_view_attrs([url(*self.args, **self.kwargs)])
        patterns_2 = apply_view_attrs([url('^xxx$', include(patterns_3), view_attrs={'level_three': 'three'})])
        patterns_1 = apply_view_attrs([url('^xxx$', include(patterns_2), view_attrs={'level_two': 'two'})])
        apply_view_attrs([url('^xxx$', include(patterns_1), view_attrs={'level_one': 'one'})])

        self.assertEqual(self.dummy_view.level_one, 'one')
        self.assertEqual(self.dummy_view.level_two, 'two')
        self.assertEqual(self.dummy_view.level_three, 'three')

    def test_override_parents_at_child_levels(self):
        kwargs = self.kwargs.copy()
        kwargs['view_attrs'] = {'four': 4444}
        patterns_3 = apply_view_attrs([url(*self.args, **kwargs)])
        patterns_2 = apply_view_attrs([url('^xxx$', include(patterns_3), view_attrs={'three': 333, 'four': 444})])
        patterns_1 = apply_view_attrs(
            [url('^xxx$', include(patterns_2), view_attrs={
                'two': 22,
                'three': 33,
                'four': 44
            })]
        )
        apply_view_attrs([url('^xxx$', include(patterns_1), view_attrs={'one': 1, 'two': 2, 'three': 3, 'four': 4})])

        self.assertEqual(self.dummy_view.one, 1)
        self.assertEqual(self.dummy_view.two, 22)
        self.assertEqual(self.dummy_view.three, 333)
        self.assertEqual(self.dummy_view.four, 4444)

    def test_remain_unaffected_if_not_nested_under_first_level(self):

        def other_dummy(request):
            pass

        kwargs = self.kwargs.copy()
        kwargs['view_attrs'] = {'four': 4444}
        patterns_6 = apply_view_attrs([url(*self.args, **kwargs)])
        patterns_5 = apply_view_attrs([url('asdf', other_dummy, **self.kwargs)])
        patterns_4 = apply_view_attrs([url('^xxx$', include(patterns_5))])
        patterns_3 = apply_view_attrs([url('^xxx$', include(patterns_6), view_attrs={'three': 333, 'four': 444})])
        patterns_2 = apply_view_attrs(
            [url('^xxx$', include(patterns_3), view_attrs={
                'two': 22,
                'three': 33,
                'four': 44
            })]
        )
        patterns_1 = apply_view_attrs([url('^xxx$', include(patterns_4))])
        apply_view_attrs(
            [
                url('^xxx$', include(patterns_2), view_attrs={
                    'one': 1,
                    'two': 2,
                    'three': 3,
                    'four': 4
                }),
                url('^xxx$', include(patterns_1))
            ]
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

        def other_dummy(request):
            pass

        kwargs = self.kwargs.copy()
        kwargs['view_attrs'] = {'four': 4444}
        patterns_6 = apply_view_attrs([url(*self.args, **kwargs)])
        patterns_5 = apply_view_attrs([url('asdf', other_dummy, **self.kwargs)])
        patterns_4 = apply_view_attrs([url('^xxx$', include(patterns_5))])
        patterns_3 = apply_view_attrs([url('^xxx$', include(patterns_6), view_attrs={'three': 333, 'four': 444})])
        patterns_2 = apply_view_attrs([url('^xxx$', include(patterns_4))])
        patterns_1 = apply_view_attrs(
            [
                url('^xxx$', include(patterns_3), view_attrs={
                    'two': 22,
                    'three': 33,
                    'four': 44
                }),
                url('^xxx$', include(patterns_2))
            ]
        )
        apply_view_attrs([url('^xxx$', include(patterns_1), view_attrs={'one': 1, 'two': 2, 'three': 3, 'four': 4})])

        self.assertEqual(other_dummy.one, 1)
        self.assertEqual(other_dummy.two, 2)
        self.assertEqual(other_dummy.three, 3)
        self.assertEqual(other_dummy.four, 4)
        self.assertEqual(self.dummy_view.one, 1)
        self.assertEqual(self.dummy_view.two, 22)
        self.assertEqual(self.dummy_view.three, 333)
        self.assertEqual(self.dummy_view.four, 4444)

    def test_get_first_and_second_level_if_nested_under_second(self):

        def other_dummy(request):
            pass

        kwargs = self.kwargs.copy()
        kwargs['view_attrs'] = {'four': 4444}
        patterns_6 = apply_view_attrs([url(*self.args, **kwargs)])
        patterns_5 = apply_view_attrs([url('asdf', other_dummy, **self.kwargs)])
        patterns_4 = apply_view_attrs([url('^xxx$', include(patterns_5))])
        patterns_3 = apply_view_attrs([url('^xxx$', include(patterns_4))])
        patterns_2 = apply_view_attrs(
            [
                url('^xxx$', include(patterns_6), view_attrs={
                    'three': 333,
                    'four': 444
                }),
                url('^xxx$', include(patterns_3))
            ]
        )
        patterns_1 = apply_view_attrs(
            [url('^xxx$', include(patterns_2), view_attrs={
                'two': 22,
                'three': 33,
                'four': 44
            })]
        )
        apply_view_attrs([url('^xxx$', include(patterns_1), view_attrs={'one': 1, 'two': 2, 'three': 3, 'four': 4})])

        self.assertEqual(other_dummy.one, 1)
        self.assertEqual(other_dummy.two, 22)
        self.assertEqual(other_dummy.three, 33)
        self.assertEqual(other_dummy.four, 44)
        self.assertEqual(self.dummy_view.one, 1)
        self.assertEqual(self.dummy_view.two, 22)
        self.assertEqual(self.dummy_view.three, 333)
        self.assertEqual(self.dummy_view.four, 4444)

    def test_get_first_and_second_and_third_level_if_nested_under_third(self):

        def other_dummy(request):
            pass

        kwargs = self.kwargs.copy()
        kwargs['view_attrs'] = {'four': 4444}
        patterns_6 = apply_view_attrs([url('asdf', other_dummy, **self.kwargs)])
        patterns_5 = apply_view_attrs([url('^xxx$', include(patterns_6))])
        patterns_4 = apply_view_attrs([url('^xxx$', include(patterns_5))])
        patterns_3 = apply_view_attrs([url(*self.args, **kwargs), url('^xxx$', include(patterns_4))])
        patterns_2 = apply_view_attrs([url('^xxx$', include(patterns_3), view_attrs={'three': 333, 'four': 444})])
        patterns_1 = apply_view_attrs(
            [url('^xxx$', include(patterns_2), view_attrs={
                'two': 22,
                'three': 33,
                'four': 44
            })]
        )
        apply_view_attrs([url('^xxx$', include(patterns_1), view_attrs={'one': 1, 'two': 2, 'three': 3, 'four': 4})])

        self.assertEqual(other_dummy.one, 1)
        self.assertEqual(other_dummy.two, 22)
        self.assertEqual(other_dummy.three, 333)
        self.assertEqual(other_dummy.four, 444)
        self.assertEqual(self.dummy_view.one, 1)
        self.assertEqual(self.dummy_view.two, 22)
        self.assertEqual(self.dummy_view.three, 333)
        self.assertEqual(self.dummy_view.four, 4444)
