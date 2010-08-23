# -*- coding: utf-8 -*-
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=80:

import feedparser
import mods
import time
import io
import re, htmlentitydefs

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

class phpBBReader(mods.Plugin):

    lastId = None

    def __init__(self, url, delay=300, channel=None):
        self.url = url
        self.delay = delay
        self.channel = channel

        try:
            with io.open('lastId','r') as file:
                c = file.read()
        except IOError, e:
            if e.errno==2:
                with io.open('lastId','w') as file:
                        file.write('None')
                c = None
            else:
                raise
        self.lastId=None

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
                    'author':   entry.author,
                    'link':     entry.link,
                    'title':    entry.title
                   })

        if firstId != None:
            self.lastId = firstId
            with io.open('lastId','w') as file:
                file.write(firstId)

        return entries

    def get_privmsgs_list(self, url=None, *args):
        messages = self.parse(url)
        if messages == 1:
            return None

        msg = []

        if len(messages)==0:
            return msg

        pattern = "[Forum] %s posted in %s - %s"
        for p in messages:
            msg.append(pattern % (p['author'],
                                  unescape(p['title']),
                                  p['link']))
        return msg

    def _get_bitly_url(self, url):
        bitly_url = "http://api.bit.ly/v3/shorten?login="


Class = phpBBReader
