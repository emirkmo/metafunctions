'''
Utility functions for use in function pipelines.
'''
import sys
import re
import functools
import typing as tp
import os

import colors

from metafunctions.core import MetaFunction
from metafunctions.core import SimpleFunction
from metafunctions.core import FunctionMerge
from metafunctions.core import CallState
from metafunctions.concurrent import ConcurrentMerge
from metafunctions.map import MergeMap
from metafunctions import operators


def node(_func=None, *, name=None, modify_tracebacks=True):
    '''Turn the decorated function into a MetaFunction.

    Args:
        _func: Internal use. This will be the decorated function if node is used as a decorator
        with no params.
        modify_tracebacks: If true, exceptions raised in composed functions have a string appended
        to them describing the location of the function in the function chain.

    Usage:

    @node
    def f(x):
       <do something cool>
    '''
    def decorator(function):
        newfunc = SimpleFunction(function, name=name, print_location_in_traceback=modify_tracebacks)
        return newfunc
    if not _func:
        return decorator
    return decorator(_func)


def bind_call_state(func):
    @functools.wraps(func)
    def provides_call_state(*args, **kwargs):
        call_state = kwargs.pop('call_state')
        return func(call_state, *args, **kwargs)
    provides_call_state._receives_call_state = True
    return provides_call_state


def star(meta_function: MetaFunction) -> MetaFunction:
    '''
    star calls its Metafunction with *x instead of x.
    '''
    fname = str(meta_function)
    #This convoluted inline `if` just decides whether we should add brackets or not.
    @node(name=f'star{fname}' if fname.startswith('(') else f'star({fname})')
    @functools.wraps(meta_function)
    def wrapper(args, **kwargs):
        return meta_function(*args, **kwargs)
    return wrapper


def store(key):
    '''Store the received output in the meta data dictionary under the given key.'''
    @node(name=f"store('{key}')")
    @bind_call_state
    def storer(call_state, val):
        call_state.data[key] = val
        return val
    return storer


def recall(key, from_call_state:CallState=None):
    '''Retrieve the given key from the meta data dictionary. Optionally, use `from_call_state` to
    specify a different call_state than the current one.
    '''
    @node(name=f"recall('{key}')")
    @bind_call_state
    def recaller(call_state, val):
        if from_call_state:
            return from_call_state.data[key]
        return call_state.data[key]
    return recaller


def concurrent(function: FunctionMerge) -> ConcurrentMerge:
    '''
    Upgrade the specified FunctionMerge object to a ConcurrentMerge, which runs each of its
    component functions in separate processes. See ConcurrentMerge documentation for more
    information.

    Usage:

    c = concurrent(long_running_function + other_long_running_function)
    c(input_data) # The two functions run in parallel
    '''
    return ConcurrentMerge(function)


def mmap(function: tp.Callable, operator: tp.Callable=operators.concat) -> MergeMap:
    '''
    Upgrade the specified function to a MergeMap, which calls its single function once per input,
    as per the builtin `map` (https://docs.python.org/3.6/library/functions.html#map).

    Consider the name 'mmap' to be a placeholder for now.
    '''
    return MergeMap(MetaFunction.make_meta(function), operator)




