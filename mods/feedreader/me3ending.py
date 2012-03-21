# -*- coding: utf-8 -*-
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=80:

import sys
import io
import time
import urllib2
import yaml

import mods

class me3ending(mods.Plugins):
    logMessage = "%d.%m.%y %H:%M:%S> Module(%(name)s): %(message)s"
    def __init__(self, shedulefn, delay=300, args={}, verbosity=False):
        mods.Plugin.__init__(self.verbosity)
        self.apiurl = "http://lugoentertainment.com/me3ending/api.php?get=%d"
        self.delay = delay
        self._shedulefn = shedulefn
        if isinstance(args, dict):
            if args.has_key('channel'):
                self.channel = args.pop('channel')
            else:
                raise mods.PluginError("Module error: broadcast channel unknow")
        else:
            raise mods.PluginError('arguments not configured')

        cookieName = 'me3ending.lasttimestamp'
        try:
            with io.open(cookieName,'r') as mfile:
                c = mfile.read()
        except IOError, e:
            with io.open(cookieName,'w') as mfile:
                mfile.write(u'None')
                c = int(time.time())

        self.vprint({'message': "timestamp set to %d" % c})
        self.lastTimestamp = c

    def get_delay(self):
        return self.delay
    def get_target(self):
        return self.target

    def parse(self, url=None):
        if url==None:
            url = self.apiUrl

        self.vprint({'message':'Parsing api feed...'})
        urlData = urllib2.urlopen(self.apiurl % self.lastTimestamp)
        if urlData.getcode() != 200:
            self.vprint({'message':"Server not ready. ERRNUM %d" % urlData.getcode()})
            return 1
        self.assetsPool = eval(urlData.read())

    def _getMsgs(self):
        entries = dict() 
        for country, assets in self.assetsPool.iteritems():
            entries.update({country: {'new':list(), 'updated':list()}})
            for asset in assets:
                points = asset.pop('points')
                last_points = asset.pop('last_point')
                asset['points'] = points - last_point
                if asset.new is 1:
                    entries[country]['new'].append(asset)
                else:
                    entries[country]['updated'].append(asset)
        return entries

    def get_scheduled_output(self, url=None, *args):
        assetList = self.parse(url)
        msg = ["News from the front !"]

        if len(messages) <= 0:
            return msg

        pattern = "%(country)s sent reinforcement to its %(asset)s, raising " \
                "its forces of %(points)s."
        patternNew = "%(country)s has got a new asset: %(asset)s"
        mpattern = "%(country)s has got several reinforcement for " \
                "multiple assets."
        mpatternNew = "%(country)s enlisted several new assets ! Now counts"\
                "%(newAssets)d more assets in the list."

        for country, assets in assetList.iteritems():
            newNum = len(assets['new'])
            updatedNum = len(assets['updated'])
            if newNum != 0:
                if newNum > 3:
                    msg.append(mpatternNew % {
                                            'country': country,
                                            'newAssets': newNum
                                            })
                    assets['new'] = list()
                    continue
                else:
                    for asset in assets:
                        msg.append(patternNew % {
                                            'country': country,
                                            'asset': asset['name']
                                            })
            if updatedNum != 0:
                if updatedNum > 3:
                    msg.append(mpattern % {'country': country})
                else:
                    for asset in assets:
                        msg.append(mpattern % {
                                        'country': country,
                                        'points': asset['point']
                                        'asset': asset['name']
                                        })
        return msg

    def vprint(self, messageDict):
        messageDict['name'] = self.name()
        formated = time.strftime(self.logMessage, time.gmtime()) % messageDict
        super(me3ending, self).vprint(formated)
