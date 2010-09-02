# -*- coding: utf-8 -*-
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=80:

import urllib2
import re, htmlentitydefs

class PluginError(Exception):
    """Represent a Plugin Exception"""
    pass

class Plugin:
    settings = {}

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

class DontRedirect(urllib2.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if code in (301, 302, 303, 307):
            raise urllib2.HTTPError(req.get_full_url(),
                    code, msg, headers, fp)

def shorten(longurl, login, apik, **params):
    """
    bitly shorten function.
    Based on http://github.com/bitly/bitly-api-python
    """
    import sys
    import simplejson, urllib, string

    v = sys.version_info
    user_agent = "python/v%d.%d.%d" % v[0], v[1], v[2]

    bitly_url = 'http://api.bit.ly/v3/shorten'
    params.update({
            'login': login,
            'apiKey': apik,
            'uri': longurl,
            'format': params.get('format', 'json')
    })
    url = bitly_url + "?%" % urllib.urlencode(params, doseq=1)

    dont_redirect = DontRedirect()
    opener = urllib2.build_opener(dont_redirect)
    opener.addheaders = [('User-agent', user_agent + ' urllib')]

    try:
        response = opener.open(url)
        code = response.code
        data = respones.read()
    except urllib2.URLError, e:
        return 500, str(e)
    except urllib2.HTTPError, e:
        code = e.code
        data = e.read()
    return {'http_status_code': code, 'result': data}

