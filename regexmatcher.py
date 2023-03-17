import re
from collections import namedtuple

"""This module contains the definitions for class regexmatcher"""

Matcher = namedtuple('Matcher', ('regex callback'))


"""regexmatcher enables matching a string against multiple regexes"""
class regexmatcher:

    """"Initialize a regexmatcher instance."""
    def __init__(self):
        self._matchers = ()


    """"Register a regex with callback. The callback will be called with a list
        containing the matched groups (could be empty) and an argument"""
    def registermatcher(self, regex, callback):
        regex_compiled = re.compile(regex)
        self._matchers += (Matcher(regex_compiled, callback),)


    """Matches to_match against all registered regexes. The associated callback
       will be called on success. Matching stops on first success.
       Returns True on success, False when no match is found."""
    def match(self, to_match, arg):
        for matcher in self._matchers:
            matched = matcher.regex.match(to_match)
            if matched:
                matcher.callback(matched, arg)
                return True
        return False
