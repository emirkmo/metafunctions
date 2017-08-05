from unittest import mock
import functools

from metafunctions.tests.util import BaseTestCase
from metafunctions.api import store, recall, node, bind_call_state
from metafunctions.util import highlight_current_function
from metafunctions.core import SimpleFunction, CallState


class TestUnit(BaseTestCase):
    def test_highlight_current_function(self):
        fmt_index = 6

        @node
        def ff(x):
            return x + 'F'

        @node
        @bind_call_state
        def f(call_state, x):
            if len(call_state._called_functions) == fmt_index:
                location_string = highlight_current_function(call_state, use_color=False)
                location_string_color = highlight_current_function(call_state, use_color=True)
                self.assertEqual(location_string, '(a | b | ff | f | f | ->f<- | f | f)')
                self.assertEqual(location_string_color,
                        '(a | b | ff | f | f | \x1b[31m->f<-\x1b[0m | f | f)')
                self.assertEqual(x, '_abFff')
            return x + 'f'

        pipe = a | b | ff | f | f | f | f | f
        pipe('_')

        state = CallState()
        af = a + f
        af('_', call_state=state)
        curr_f = highlight_current_function(state, use_color=False)
        self.assertEqual(curr_f, '(a + ->f<-)')

    @mock.patch('metafunctions.util.highlight_current_function')
    def test_highlight_current_function_multichar(self, mock_h):
        mock_h.side_effect = functools.partial(highlight_current_function, use_color=False)
        # Don't fail on long named functions. This is a regression test
        @node
        def fail(x):
            if not x:
                1 / 0
            return x - 1

        cmp = fail | fail + a

        with self.assertRaises(ZeroDivisionError) as e:
            cmp(1)
        self.assertTrue(e.exception.args[0].endswith('(fail | (->fail<- + a))'))

    def test_highlight_with_map(self):
        self.fail('todo')

    def test_raise_with_call_state(self):
        # raise_with_call_state is a context manager that catches any exception generated by the
        # metafunction
        self.fail('todo')

@node
def a(x):
    return x + 'a'
@node()
def b(x):
    return x + 'b'
@node()
def c(x):
    return x + 'c'
