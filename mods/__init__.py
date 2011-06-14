# -*- coding: utf-8 -*-
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=80:

import re
import htmlentitydefs


class PluginError(Exception):
    """Represent a Plugin Exception"""
    pass

class Plugin:
    import sys as __sys
    settings = {}

    def __init__(self, verbosity=0, log=__sys.stderr):
        self.__verbosity = verbosity
        self.__log = log

    def vprint(self, msg):
        self.verbose(1, msg)

    def dprint(self, msg):
        self.verbose(2, msg)

    def verbose(self, verbosity, msg):
        if verbosity <= self.__verbosity:
            print >> self.__log,'*' * verbosity, msg

    def name(self):
        return self.__class__.__name__

    def config(self, key):
        if self.settings.has_key(key):
            return self.settings[key]

def unescape(text):
    """
    Removes HTML or XML character references and entities from a text string.
    Borrowed from http://effbot.org/zone/re-sub.htm#unescape-html

    @param text The HTML (or XML) source text.
    @return The plain text, as a Unicode string, if necessary
    """
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)


