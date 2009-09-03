###
# Copyright (c) 2009, Dag Odenhall
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

import re
from camxes import Camxes

try:
    reload(jbovlaste)
except:
    import jbovlaste

class Makfa(callbacks.Plugin):
    """Add the help for "@plugin help Makfa" here
    This should describe *how* to use this plugin."""

    def __init__(self, irc):
        self.__parent = super(Makfa, self)
        self.__parent.__init__(irc)
        self.db = jbovlaste.Dictionary('data/jbovlaste-en.xml')
        self._camxes = Camxes()

    def unnest(self, irc, msg, args, command):
        """<command>

        Execute a command and get the non-nested output.
        """
        self.Proxy(irc.irc, msg, callbacks.tokenize(command))
    unnest = wrap(unnest, ['text'])

    def unquote(self, irc, msg, args, opts, text):
        """[--number <integer>] <text>

        Extract the contents of a Lojban quote in a text,
        defaults to the last one (--number 0).
        """
        number = -1
        for (key, val) in opts:
            if key == 'number':
                number = val - 1
        if '{' in text:
            irc.reply(re.findall(r'\{(.+?)\}', text)[number])
        else:
            irc.reply(text)
    unquote = wrap(unquote, [getopts({'number': 'int'}), 'text'])

    def _cenlai(self, text):
        tokens = text.lower().replace('.', ' ').split()
        hit = [i in self.db for i in tokens]
        percentage = int(float(hit.count(True)) / len(tokens) * 100)
        return percentage

    def lastlojban(self, irc, msg, args, channel, nick, percent):
        """[channel] [nick] [percent]

        Get the last Lojban message as determined by potential-percentage.
        """
        if not percent:
            percent = 40
        for ircmsg in reversed(irc.state.history):
            if ircmsg.command == 'PRIVMSG':
                msgs = [ircmsg.args[1]]
                if '{' in msgs[0]:
                    msgs = reversed(list(re.findall(r'\{(.+?)\}', msgs[0])))
                for imsg in msgs:
                    if self._cenlai(imsg) >= percent:
                        if not channel or \
                           ircutils.strEqual(channel, ircmsg.args[0]):
                            if not nick or \
                               ircutils.hostmaskPatternEqual(nick,
                                                             ircmsg.nick):
                                irc.reply(imsg)
                                return
    lastlojban = wrap(lastlojban, [optional('channel'),
                                   optional('seenNick'),
                                   optional('positiveInt')])

    def camxes(self, irc, msg, args, text):
        """<text>

        Get the grammatical portion of text with camxes.
        """
        grammatical = self._camxes.parse(text)
        result = grammatical + '\x0304' + text[len(grammatical):] + '\x03'
        irc.reply(result)
    camxes = wrap(camxes, ['text'])


Class = Makfa


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
