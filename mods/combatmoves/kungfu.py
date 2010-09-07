# -*- coding: utf-8 -*-
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=80:

import random
import mods
import moves
from irclib.irclib import nm_to_n

class kungfu(mods.Plugin):

    hit_power = {
        'critical':  0x0010,
        'normal':    0x0011,
        'powerless': 0x0012,
        'missed':    0x0013
    }
    logMessage = "%d.%m.%y %H:%M:%S> Module(%(name)s): %(message)s"

    def __init__(self, config):
        self.settings = config
        # this is the irc message body, not the corpse
        self.body = None
        self._location = ['TOP','LEFT','RIGHT', 'MIDDLE', 'BOTTOM', 'CENTRAL']

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

        if self.body[0] == ':':
            pass # special commands
        elif self.settings['nickname'].lower() in self.body.lower():
            for move, actions in moves.attacks.iteritems():
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


    def _check_hit(self, critical, fail, miss):
        """
        Check if and with how much power a hit is done
        """
        random.seed()
        rnumber = random.randint(1, 100)
        print time.strftime(self.logMessage, time.gmtime()) % {
                'name': self.name(),
                'message': 'roll is '+rnumber
        }

        if rnumber >= critical:
            return self.hit_power['critical']
        elif miss < rnumber < fail:
            return self.hit_power['powerless']
        elif rnumber < fail:
            return self.hit_power['missed']
        else:
            return self.hit_power['normal']

    def process_kick(self, actions):
        for part in moves.bodyparts.iterkeys():
            if part in self.body:
                cbodyparts = moves.bodyparts[part]
                if list(set(cbodyparts+self._location)-set(cbodyparts)) != []:
                    cbodyparts = list(cbodyparts + moves.bodyparts[part])
                    modifier = 1.5
                else:
                    modifier = 0

                # TOP meaning 'head' and hard to touch
                if 'TOP' in cbodyparts:
                    hit = self._check_hit(90, 40*modifier, 10*modifier)
                elif 'CENTRAL' in cbodyparts or 'MIDDLE' in cbodyparts:
                    hit = self._check_hit(80, 30*modifier, 5*modifier)
                elif 'BOTTOM' in cbodyparts:
                    hit = self._check_hit(90, 30*modifier, 10*modifier)

        try:
            hit
        except:
            self.body = self.body + " " + random.choice(moves.bodyparts.keys())
            return self.process_kick(actions)


        if hit == self.hit_power['powerless']:
            return "Ah ah, that kick doesn't even frighten a bug !"
        elif hit == self.hit_power['missed']:
            return "Improve your AIM - Improve yourself. " \
                   "You just missed me, faggot !"
        elif hit == self.hit_power['critical']:
            return "Yeah, thanks to you. You just successfuly hit my "+part+'.'
        elif hit == self.hit_power['normal']:
            return 'Ouch, that hurt !'

Class=kungfu
