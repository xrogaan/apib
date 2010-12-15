# -*- coding: utf-8 -*-
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=80:

import yaml
import mods.Plugins

class factoidsLoader(mods.PLugin):
    factoidsFile = 'factoids.yaml'

    def __init__(self, shedulefn, args={}):
        self._shedulefn = shedulefn

        self.rawdata = yaml.load(open(self.factoidsFile, 'rb').read())
        self.rawdata.update({
            'add': "this command isn't implemented yet."
        })

    def _save_factoids(self):
        filestream = open(self.factoidsFile, 'w')
        yaml.dump(self.rawdata, filestream.write)
        filestream.close()

    def on_privmsg(self, c, e):
        self._on_msg(c, e)

    def on_pubmsg(self, c, e):
        self._on_msg(c, e)

    def _on_msg(self, c, e):
        source = nm_to_n(e.source())
        target = e.target()

        self.body = e.arguments()[0]
        if self.body[0] == ":":
            for (key, action) in self.rawdata.iteritems:
                if self.body.startswith(':%s' % key):
                    c.privmsg(target, action)
                    return

Class=factoidsLoader
