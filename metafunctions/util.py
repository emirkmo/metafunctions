'''Utilities for working with MetaFunctions'''
import os
import sys
import re

import colors

def _system_supports_color():
    """
    Returns True if the running system's terminal supports color, and False otherwise. Originally
    from Django, by way of StackOverflow: https://stackoverflow.com/a/22254892/1286571
    """
    plat = sys.platform
    supported_platform = plat != 'Pocket PC' and (plat != 'win32' or 'ANSICON' in os.environ)
    # isatty is not always implemented, #6223.
    is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    if not supported_platform or not is_a_tty:
        return False
    return True


def highlight_current_function(call_state, color=colors.red, use_color=_system_supports_color()):
    '''Return a formatted string showing the location of the currently active function in call_state.

    Consider this a 'you are here' when called from within a function pipeline.
    '''
    current_name = str(call_state._called_functions[-1])

    # how many times will current_name appear in str(call_state._meta_entry)?
    # Bearing in mind that pervious function names may contain current_name
    num_occurences = sum(str(f).count(current_name) for f in call_state._called_functions)

    # There's probably a better regex for this.
    regex = f"((?:.*?{current_name}.*?){{{num_occurences-1}}}.*?){current_name}(.*$)"

    highlighted_name = f'->{current_name}<-'
    if use_color:
        highlighted_name = color(highlighted_name)

    highlighted_string = re.sub(regex, fr'\1{highlighted_name}\2', str(call_state._meta_entry))
    return highlighted_string
