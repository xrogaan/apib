# -*- coding: utf-8 -*-
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=80:

import feedparser
import mods

class phpBBReader(mods.Plugin):

    lastId = None

    def __init__(self, url, delay=300):
        self.url = url
        self.delay = delay
        pass

    def register_hook(self):
        return ()

    def parse(self, url=None):
        if url == None:
            url = self.url
        self.parser = feedparser.parse(url)

        if self.parser.bozo != 0:
            urlError = self.parser.bozo_exception
            print "Warning: bozo error in effect!!!"
            print ">>> (%s) %s" % (urlError.reason[0],urlError.reason[1])
            return 1

        if self.parser.status == 404:
            print "Warning: the feed '%s' could not be found. 404 Error" % url
            return 1

        return self.getMsgs()

    def getMsgs(self):
        firstId = None
        entries = []

        for entry in self.parser['entries']:
            if self.lastId == entry.id:
                break
            elif firstId == None:
                firstId = entry.id

            entries.append({
                    'author': entry.author,
                    'link':   entry.link,
                    'title':  entry.title
                   })

        if firstId != None:
            self.lastId = firstId
        return entries


Class = phpBBReader
