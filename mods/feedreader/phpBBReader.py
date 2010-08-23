# -*- coding: utf-8 -*-
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=80:

import feedparser
import mods
import time

class phpBBReader(mods.Plugin):

    lastId = None

    def __init__(self, url, delay=300, channel=None):
        self.url = url
        self.delay = delay
        self.channel = channel
        pass

    def get_delay(self):
        return self.delay

    def get_target(self):
        return self.channel

    def parse(self, url=None):
        if url == None:
            url = self.url

        t = time.strftime("%d.%m.%y %H:%M:%S> Module(%(name)s): Parsing feed..." , time.gmtime())
        t = t % {'name':self.name()}
        print t
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
            if self.lastId == entry.id:
                break
            elif firstId == None:
                firstId = entry.id

            verbose = "Module(%(name)s): New message -> %(url)s" % {
                                        'name': self.name(),
                                        'url': entry.link
                                    }
            print verbose
            entries.append({
                    'author':   entry.author.encode('UTF-8'),
                    'category': entry.category.encode('UTF-8'),
                    'link':     entry.link.encode('UTF-8'),
                    'title':    entry.title.encode('UTF-8')
                   })

        if firstId != None:
            self.lastId = firstId
        return entries

    def get_privmsgs_list(self, url=None, *args):
        messages = self.parse(url)
        if messages == 1:
            return None

        msg = []

        if len(messages)==0:
            return msg

        pattern = "[Forum] %s posted in %s " + unichr(8226) + " %s - %s "
        for p in messages:
            msg.append(pattern % (p['author'].decode('UTF-8'),
                                  p['category'].decode('UTF-8'),
                                  p['title'].decode('UTF-8'),
                                  p['link'].decode('UTF-8')))
        return msg

    def _get_bitly_url(self, url):
        bitly_url = "http://api.bit.ly/v3/shorten?login="


Class = phpBBReader
