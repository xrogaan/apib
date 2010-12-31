# -*- coding: utf-8 -*-
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=80:

import yaml
import mods.Plugins

class factoidsLoader(mods.Plugin):
    factoidsFile = 'factoids.yaml'

    def __init__(self, shedulefn, args={}):
        """
        This will simply load the factoids. The yaml file must be in the proper
        format for that. Extra test could be usefull.
        """
        self._shedulefn = shedulefn
        self._fSpecials = [
                'add',
                'save',
                'load'
        ]

        self._load_factoids()

    def _load_factoids(self):
        self.rawdata = yaml.load(open(self.factoidsFile, 'rb').read())
        for fSpecial in self._fSpecial:
            self.rawdata.update({fSpecial: "This command is special."})

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

    def _do_special(self, body):
        """
        Call special action for special commands.
        """
        for fSpecial in self._fSpecial:
            if body.startswith(':%s' % fSpecial):

                fAttr = '_do_%s' % fSpecial

                if not hasattr(self, fAttr):
                    raise AttributeError(
                        "Trying to call %s but doesn't exist." % fAttr
                    )
                else:
                    getattr(self, fAttr)(body.split(None, 2))

    def _do_save(self, nothing):
        self._save_factoids()

    def _do_load(self, nothing):
        self._load_factoids()

    def _do_add(self, data):
        self.rawdata.update({data[2]: data[3]})

Class=factoidsLoader
