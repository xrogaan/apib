# -*- coding: utf-8 -*-
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=80:

class Plugin:

    def name(self):
        return self.__class__.__name__


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
    import urllib2

    v = sys.version_info
    user_agent = "python/v%d.%d.%d" % v[0], v[1], v[2]

    bitly_url = 'http://api.bit.ly/v3/shorten'
    params.update({
            'login': login,
            'apiKey': apik,
            'uri': longurl
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

