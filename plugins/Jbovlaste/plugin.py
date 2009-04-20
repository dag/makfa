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
from lxml import etree
from os import path
import re


class Jbovlaste(callbacks.Plugin):
    """Add the help for "@plugin help Jbovlaste" here
    This should describe *how* to use this plugin."""

    def __init__(self, irc):
        self.__parent = super(Jbovlaste, self)
        self.__parent.__init__(irc)
        self.tree = etree.parse(path.dirname(path.abspath(__file__)) +
                                "/xml-export.html")

    def selmaho(self, irc, msg, args, valsi):
        try:
            tmp = self.tree.find('//valsi[@word="%s"]/selmaho' % valsi).text
            irc.reply(tmp)
        except:
            irc.reply('(none)')
    selmaho = wrap(selmaho, ['text'])

    def rafsi(self, irc, msg, args, valsi):
        lst = self.tree.xpath('//valsi[@word="%s"]/rafsi/text()' % valsi)
        if len(lst) > 0:
            irc.reply(', '.join(lst))
        else:
            irc.reply('(none)')
    rafsi = wrap(rafsi, ['text'])

    def definition(self, irc, msg, args, valsi):
        try:
            defn = self.tree.find('//valsi[@word="%s"]/definition' % valsi).text
            irc.reply(re.sub(r'\$[a-z]+_\{?(\d+)\}?\$', r'x\1', defn))
        except:
            irc.reply('(none)')
    definition = wrap(definition, ['text'])

    def notes(self, irc, msg, args, valsi):
        try:
            note = self.tree.find('//valsi[@word="%s"]/notes' % valsi).text
            irc.reply(re.sub(r'\$[a-z]+_\{?(\d+)\}?\$', r'x\1', note))
        except:
            irc.reply('(none)')
    notes = wrap(notes, ['text'])

    def gloss(self, irc, msg, args, valsi):
        try:
            tmp = self.tree.find('//nlword[@valsi="%s"]' % valsi).get("word")
            irc.reply(tmp)
        except:
            irc.reply('(none)')
    gloss = wrap(gloss, ['text'])

    def find(self, irc, msg, args, opts, valsi):
        try:
            if ('rafsi', True) in opts:
                all = self.tree.findall('//valsi/rafsi')
                for afx in all:
                    if afx.text == valsi:
                        irc.reply(afx.getparent().get("word"))
            elif ('selmaho', True) in opts:
                all = self.tree.findall('//valsi/selmaho')
                lst = []
                for semao in all:
                    if semao.text == valsi.upper():
                        lst.append(semao.getparent().get("word"))
                irc.reply(', '.join(lst))
            else:
                v = self.tree.find('//nlword[@word="%s"]' % valsi).get("valsi")
                irc.reply(v)
        except:
            irc.reply('(not found)')
    find = wrap(find, [getopts({'rafsi': '', 'selmaho': ''}), 'text'])


Class = Jbovlaste


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
