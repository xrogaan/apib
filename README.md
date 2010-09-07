 apib: the schyzophrenic irc bot
=================================

This is just a little irc bot to entertain my python skills.

 Configuration
---------------

To configure the bot, you'll need to copy `contrib/config.yaml.dist` to the
root directory and edit it.

**Basic configuration:**

*  servers: IRC Server to connect to. The prefix `!!python/tulpe` is required.
*  channels: channels in the auto-join list. Format <*List*>
   `['#channel1','#channel2','#channeln']`
*  nickname: Name of the bot. Format <*String*>
*  quitmsg: quit message. Format <*String*>
*  owners: list of know owners. Format <*List*> `['owner1','owner2','ownern']`
*  password: master password. Format <*String*>

There are modules who needs their own parameters. I'll create a wiki page for
them when I have time.

 Python irclib
===============

This application include a modified version of the Python IRC library
(irclib.py). You can view the sources files in the subdirectory irclib/

They are hosted at sourceforge : http://python-irclib.sourceforge.net/
