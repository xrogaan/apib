# -*- coding: utf-8 -*-
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=80:

import random
import mods
import mods.kungfu.moves as moves

class kungfu(mods.Plugin):

    hit_power = {
        'critical':  0x0010,
        'normal':    0x0011,
        'powerless': 0x0012,
        'missed':    0x0013
    }

    def __init__(self):
        self.body = None
        pass

    def on_privmsg(self, c, e):
        self._on_msg(c, e)

    def on_pubmsg(self, c, e):
        self._on_msg(c, e)

    def _on_msg(self, c, e):
        source = nm_to_n(e.source())
        target = e.target()

        self.body = e.arguments()[0]
        if self.body == '' or self.body[0] == "<" or self.body[0:1] == " <":
            return

        if self.body[0] = ':':
            pass # special commands
        elif self.settings['nickname'].lower() in self.body:
            for move, actions in moves.attack:
                if move in self.body:
                    handler = "process_" + move
                    if hasattr(self, handler):
                        c.privmsg(target, getattr(self,handler)(actions))
                    else:
                        c.privmsg(target,
                                  "I'm supposed to know how to handle " \
                                  "this, but my creator is a lazy bastard " \
                                  "and didn't teach me how to kick your ass.")
                        c.privmsg(target,
                                  "And by the way, stop hitting me. It hurts!")

    def process_kick(self, actions):
        random.seed()
        rnumber = random.randint(1,100)
        for part in moves.bodyparts.iterkeys():
            if part in self.body:
                if 'TOP' in moves.bodyparts[part]:
                    if rnumber >= 80:
                        hit = self.hit_power['critical']
                    elif rnumber >= 60:
                        hit = self.hit_power['normal']
                    elif 20 < rnumber < 60:
                        hit = self.hit_power['powerless']
                    else:
                        hit = self.hit_power['missed']
        return ""

Class=kungfu
