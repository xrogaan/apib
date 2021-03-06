#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=80:

__version__="0.2.1-dev"

import os
import sys
import imp
import traceback
import time
from types import *

try:
    import yaml
except ImportError:
    print "Error: PyYAML is missing. - http://pyyaml.org/wiki/PyYAML"
    sys.exit(1)

try:
    from irclib.irclib import *
    from irclib.ircbot import *
except ImportError:
    print "Error: irclib and ircbot not found."
    print "Please, install them."
    print "http://python-irclib.sourceforge.net/"
    sys.exit(1)

def loadModule(name):
    dir = ["./mods"]
    modInfo = imp.find_module(name, dir)
    try:
        module = imp.load_module(name, *modInfo)
    except:
        sys.modules.pop(name, None)
        raise
    if module.__name__ in sys.modules:
        sys.modules[module.__name__] = module
    return module

def loadModuleClass(module, obj, shedulefn, args=()):
    try:
        args = list(args)
        args.insert(0, shedulefn)
        curMod = module.Classes[obj](*args)
    except AttributeError, e:
        if 'Class' in str(e):
            print "I just don't know which 'Class' " \
                  "to instanciate for module %s" % (module)
            sys.exit(1)
        else:
            raise
    curMod.classModule = module
    return curMod

def get_time():
    """
    Return time as a nice yummy string
    """
    return time.strftime("%H:%M:%S",
            time.localtime(time.time()))

class Apib(SingleServerIRCBot):

    ownermask = []

    commanddict = {
            "die": "Special command, makes the bot suicidal.",
            "join": "Makes the bot walk through other channels. Like they " \
                    " want him ...",
            "part": "Takes back the bot from others channels.",
            "nick": "Funny part, he could want to be Napoleon...",
            "quitmsg": "Set the quit message. Without arguments show the " \
                       "current one",
            "talk": "As if he did not talk enough ...",
            "owner": "With this, you could become a nurse."
    }

    def __init__(self, config):
        self.settings = config
        self.chans    = config['channels']
        self.owners   = config['owners']
        self.rebel    = None
        self.modules  = {}

    def _modules_dispatcher(self, c, e):
        m = "on_" + e.eventtype()
        for key,mod in self.modules.iteritems():
            if mod.config('handle') == 'to_dispatch' and hasattr(mod, m):
                getattr(mod, m)(c, e)

    def our_start(self):
        print "Connecting to server..."
        SingleServerIRCBot.__init__(self, config['servers'],
                                          config['nickname'],
                                          config['nickname'])

        print "Loading extra modules..."
        for mod in self.settings['modules']:
            print '>'*3,' %s ...' % (mod['subname'])
            args = list(mod['args'])
            args.append({'verbose': self.settings['verbose']})
            mod['args'] = args
            self.modules.update({
                mod['subname']:
                  loadModuleClass(
                      loadModule(mod['name']),
                      mod['subname'],
                      self.owners,
                      mod['args']
                  )
            })
            del(args)

            if self.modules[mod['subname']].config('handle') == 'scheduled':
                self.ircobj.execute_scheduled(
                        mod['args'][1], # delay
                        self.m_privmsg,
                        (
                            self.modules[mod['subname']].get_scheduled_output,
                            self.modules[mod['subname']].get_target(),
                            self.connection
                        )
                )
                print '>'*3,' %s is scheduled' % (mod['subname'])

        self.start()

    def on_nicknameinuse(self, c, e):
        self.settings['nickname'] = c.get_nickname() + "_"
        c.nick(self.settings['nickname'])

    def on_welcome(self, c, e):
        print "Joining channels..."
        print self.chans
        for chan in self.chans:
            c.join(chan)


    def on_privmsg(self, c, e):
        self._on_msg(c, e)

    def on_pubmsg(self, c, e):
        # Parse Nickname!username@host.mask.net to Nickname
        self._on_msg(c, e)

    def _on_msg(self, c, e):
        """
        Internal.
        Process messages.
        """
        # Parse Nickname!username@host.mask.net to Nickname
        source = nm_to_n(e.source())
        target = e.target()

        # First message from owner 'locks' the owner host mask
        # Borrowed from pyborg.
        if not e.source() in self.ownermask and source in self.owners:
            self.ownermask.append(e.source())
            print "Locked on %s. Waiting orders..." % e.source()

        body = e.arguments()[0]
        for irc_color_char in [',', "\x03"]:
            debut = body.rfind(irc_color_char)
            if 0 <= debut < 5:
                x = 0
                for x in range(debut+1, len(body)):
                    if body[x].isdigit() == 0:
                        break
                body = body[x:]

        #remove special irc fonts chars
        body = body[body.rfind("\x02")+1:]
        body = body[body.rfind("\xa0")+1:]

        if body == '' or body[0] == "<" or body[0:1] == " <":
            return

        commands = body.split()
        commands[0] = commands[0].lower()

        if (body[0] == ':' or
            body.find(self.settings['nickname'].lower()) != -1):
            self.do_commands(commands, source, target, c, e)

    def do_commands(self, command_list, source, target, c, e):
        """
        General irc commands
        """
        if e.eventtype() == "privmsg":
            self.do_private_commands(command_list, source, target, c, e)

        # Huh, you're talking to me ?!
        if source in self.owners and command_list[0] == ':die':
            print "> system going down..."
            sys.exit()

    def do_private_commands(self, command_list, source, target, c, e):
        """
        Special irc commands
        """
        # set owner credentials
        if (command_list[0] == ':owner' and len(command_list) > 1 and
            source not in self.owners):
            if command_list[1] == self.settings['password']:
                self.owners.append(source)
                self.output("Lucky you! Now I want to eat something.",
                           ("", source, target, c, e))
            else:
                self.output("No, you can't have my cookie. IT'S MINE!!!",
                           ("", source, target, c, e))

        elif source in self.owners:
            # change nickname
            if command_list[0] == ':nick':
                try:
                    self.connection.nick(command_list[1])
                    self.settings['nickname'] = command_list[1]
                except:
                    pass

            # join other channels
            elif command_list[0] == ':join':
                for i in range(1, len(command_list)):
                    if not command_list[i] in self.chans:
                        self.chans.append(command_list[i])
                        c.join(command_list[i])

            # part from other channels
            elif command_list[0] == ':part':
                for i in range(1, len(command_list)):
                    if command_list[i] in self.chans:
                        self.chans.remove(command_list[i])
                        c.part(command_list[i])

    def get_version(self):
        return "apib v%s, the schizophrenic ircbot" % __version__

    def m_privmsg(self, messages, target, c):
        messages = messages()
        for msg in messages:
            print "> Sending message: %s" % msg.encode('UTF-8', 'replace')
            c.privmsg(target, msg.encode('UTF-8', 'replace'))
            time.sleep(3)

    def output(self, message, args):
        """
        Output a line of text. args = (body, source, target, c, e)
        Borrowed from pyborg. Thanks to them
        """
        if not self.connection.is_connected():
            print "Can't send reply : not connected to server"
            return

        # Unwrap arguments
        body, source, target, c, e = args

        # Decide. should we do a ctcp action?
        if message.find(self.settings['nickname'].lower()+" ") == 0:
            action = 1
            message = message[len(self.settings['nickname'])+1:]
        else:
            action = 0

        # Joins replies and public messages
        if (e.eventtype() == "join" or e.eventtype() == "quit" or
            e.eventtype() == "part" or e.eventtype() == "pubmsg"):
            if action == 0:
                print "[%s] <%s> > %s> %s" % (get_time(),
                                              self.settings['nickname'],
                                              target, message)
                c.privmsg(target, message)
            else:
                print "[%s] <%s> > %s> /me %s" % (get_time(),
                                                  self.settings['nickname'],
                                                  target, message)
                c.action(target, message)
        # Private messages
        elif e.eventtype() == "privmsg":
            # normal private msg
            if action == 0:
                print "[%s] <%s> > %s> %s" % ( get_time(),
                            self.settings['nickname'], source, message)
                c.privmsg(source, message)
                # send copy to owner
                if not source in self.owners:
                    c.privmsg(','.join(self.owners),
                              "(From "+source+") "+body)
                    c.privmsg(','.join(self.owners),
                              "(To   "+source+") "+message)
            # ctcp action priv msg
            else:
                print "[%s] <%s> > %s> /me %s" % (get_time(),
                                                  self.settings['nickname'],
                                                  target, message)
                c.action(source, message)
                # send copy to owner
                if not source in self.owners:
                    map ((lambda x: c.action(x, "(From "+source+") "+body)), self.owners)
                    map ((lambda x: c.action(x, "(To   "+source+") "+message)), self.owners)

if __name__ == "__main__":
    from optparse import OptionParser

    usage = "Usage: %prog [-s <server> [-p <port>]] [-c <channel>] config.yaml"
    parser = OptionParser(usage=usage, version="%prog "+__version__,
                          description="A schizophrenic irc bot.")

    parser.add_option("-s", "--server",
                      metavar="SERVERAME", help="Server adress to connect to")

    parser.add_option("-p", "--port",
                      metavar="PORT", help="Port number to connect to")

    parser.add_option("-c", "--channel",
                      metavar="CHANNEL", help="Join CHANNEL on connect")

    parser.add_option('-v', '--verbose', action="store_true", default=False,
                     metavar="VERBOSE", help="To be more speaky")

    (cfg, arguments) = parser.parse_args()
    if len(arguments) != 1:
        parser.error("incorrect number of arguments")

    configFile = os.path.abspath(os.path.normpath(arguments[0]))
    if not os.path.exists(configFile):
        parser.error("config file not found")

    config = yaml.load(open(configFile, 'rb').read())
    config.setdefault('channels', [])
    config.setdefault('owners', [])
    config.setdefault('nickname', 'apib')
    config.setdefault('verbose', cfg.verbose)

    if cfg.server is not None:
        config['servers'].append((cfg.server,
                                  cfg.port if cfg.port is not None else 6667))
    if cfg.channel is not None:
        config['channels'].append(cfg.channel)

    # Be sure to have a port to connect to
    if 'servers' in config:
        for s in config['servers']:
            if len(s) == 1:
                s.append(6667)

    bot = Apib(config)

    try:
        bot.our_start()
    except KeyboardInterrupt, e:
        pass
    except SystemExit, e:
        pass
    except:
        traceback.print_exc()
        sys.exit(0)

    bot.disconnect(bot.settings['quitmsg'])

