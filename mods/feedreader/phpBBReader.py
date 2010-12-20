# -*- coding: utf-8 -*-
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=80:

import sys
import time
import io
import re
import urllib2

try:
    import feedparser
except ImportError:
    print('Error: feedparser not found. Please install it.')
    print('Feedparser website: http://feedparser.org/')
    exit(1)

import mods


class DontRedirect(urllib2.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if code in (301, 302, 303, 307):
            raise urllib2.HTTPError(req.get_full_url(),
                    code, msg, headers, fp)


class phpBBReader(mods.Plugin):

    lastId = None
    logMessage = "%d.%m.%y %H:%M:%S> Module(%(name)s): %(message)s"

    def __init__(self, shedulefn, url, delay=300, args={}):
        self.url = url
        self.delay = delay
        self._shedulefn = shedulefn
        self.forums_ignore = []
        if isinstance(args, dict):
            if args.has_key('channel'):
                self.channel = args.pop('channel')
            else:
                raise mods.PluginError("Module error: required argument "\
                                       "`channel` is missing.")

            if args.has_key('ignore'):
                if isinstance(args['ignore'], list):
                    for v in args['ignore']:
                        self.forums_ignore.append(v)
                    del args['ignore']
                else:
                    self.forums_ignore.append(args.pop('ignore'))

            if args.has_key('bitly'):
                self._use_bitly = True
                self._bitly_settings = args['bitly']
            else:
                self._use_bitly = False

            self.settings = args
        else:
            raise mods.PluginError, "not well configured"

        try:
            with io.open('lastId','r') as file:
                c = file.read()
        except IOError, e:
            if e.errno==2:
                with io.open('lastId','w') as file:
                        file.write(u'None')
                c = None
            else:
                raise

        print time.strftime(self.logMessage, time.gmtime()) % {
                'message': "lastId set to %s" % c, 'name': self.name()
        }

        self.lastId=c

        pass

    def get_delay(self):
        return self.delay

    def get_target(self):
        return self.channel

    def parse(self, url=None):
        if url == None:
            url = self.url

        print time.strftime(self.logMessage, time.gmtime()) % {
                'name':self.name(), 'message': "Parsing feed..."
        }

        self.parser = feedparser.parse(url)

        if self.parser.bozo != 0:
            urlError = self.parser.bozo_exception
            print "Warning: bozo error in effect!!!"
            print ">>> (%s) %s" % (urlError.reason[0],urlError.reason[1])
            return 1

        if self.parser.status == 404:
            print "Warning: the feed '%s' could not be found. 404 Error" % url
            return 1

        return self._getMsgs()

    def _getMsgs(self):
        firstId = None
        entries = []

        for entry in self.parser['entries']:
            # We do not want to loop on a already sent data
            if self.lastId == entry.id:
                break

            # Attempt to ignore designed forums
            if len(self.forums_ignore) is not 0:
                breakit = False
                try:
                    url = entry.tags[0]['scheme']
                    fid = re.search('f=([0-9]+)$',url)
                    fid = int(fid.groups()[0])
                except:
                    pass
                else:
                    if fid in self.forums_ignore:
                        breakit = True
                finally:
                    del url

                if breakit:
                    print time.strftime(self.logMessage, time.gmtime()) % {
                            'name':self.name(),
                            'message': "post ignored: %d" % fid
                    }
                    continue

            # If we don't have any id in memory, that's because there is no
            # history
            if firstId == None:
                firstId = entry.id

            verbose = "Module(%(name)s): New message -> %(url)s" % {
                                        'name': self.name(),
                                        'url': entry.link
                                    }
            print verbose
            entries.append({
                    'author':   entry.author,
                    'link':     entry.link,
                    'title':    entry.title
                   })

        if firstId != None:
            self.lastId = firstId
            with io.open('lastId','w') as file:
                file.write(firstId)

        entries.reverse()
        return entries

    def get_scheduled_output(self, url=None, *args):
        messages = self.parse(url)
        if messages == 1:
            return None

        msg = []

        if len(messages)==0:
            return msg

        pattern = "[off][Forum] %s posted in %s - %s"
        for p in messages:
            msg.append(pattern % (p['author'],
                                  mods.unescape(p['title']),
                                  self._get_bitly_url(p['link'])
                                 )
                      )
        return msg

    def _get_bitly_url(self, longurl):
        if self._use_bitly:
            import simplejson
            rawjson = self.shorten(longurl)
            result = simplejson.loads(rawjson['result'])

            if result['status_code'] is not 200:
                print time.strftime(self.logMessage, time.gmtime()) % {
                    'message': "bitly error: %s" % result['status_txt'],
                    'name': self.name()
                }
                return longurl

            else:
                return result['data']['url']

        else:
            return longurl

    def shorten(self, longurl):
        """
        bitly shorten function.
        Based on http://github.com/bitly/bitly-api-python
        """
        import urllib

        v = sys.version_info
        try:
            user_agent = "python/v%d.%d.%d" % (v[0], v[1], v[2])
        except TypeError, e:
            user_agent = "python/v%d.%d.%d" % (v['major'], v['minor'],
                                               v['micro'])

        bitly_url = 'http://api.bit.ly/v3/shorten'
        params = dict({
            'login': self._bitly_settings['login'],
            'apiKey': self._bitly_settings['apiKey'],
            'uri': longurl,
            'format': 'json'
        })
        url = bitly_url + "?%s" % urllib.urlencode(params, doseq=1)

        dont_redirect = DontRedirect()
        opener = urllib2.build_opener(dont_redirect)
        opener.addheaders = [('User-agent', user_agent + ' urllib')]

        try:
            response = opener.open(url)
            code = response.code
            data = response.read()
        except urllib2.URLError, e:
            code = 500
            data = str(e)
        except urllib2.HTTPError, e:
            code = e.code
            data = e.read()
        return {'http_status_code': code, 'result': data}

Class = phpBBReader
