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
import random
from jbovlaste import Dictionary


class Jbovlaste(callbacks.Plugin):
    """Add the help for "@plugin help Jbovlaste" here
    This should describe *how* to use this plugin."""

    def __init__(self, irc):
        self.__parent = super(Jbovlaste, self)
        self.__parent.__init__(irc)
        self.db = Dictionary('data/jbovlaste-en.xml')

    def selmaho(self, irc, msg, args, valsi):
        """<entry>

        Get the selma'o of a cmavo or cmavo cluster.
        """
        if valsi in self.db:
            if self.db[valsi].selmaho:
                irc.reply(self.db[valsi].selmaho)
            else:
                irc.reply("no selma'o")
        else:
            irc.reply('no entry')
    selmaho = wrap(selmaho, ['text'])

    def rafsi(self, irc, msg, args, valsi):
        """<word>

        Get the rafsi of a word.
        """
        if valsi in self.db:
            if self.db[valsi].rafsi:
                irc.reply(', '.join(self.db[valsi].rafsi))
            else:
                irc.reply("no rafsi")
        else:
            irc.reply('no entry')
    rafsi = wrap(rafsi, ['text'])

    def definition(self, irc, msg, args, valsi):
        """<entry>

        Get the definition for an entry.
        """
        if valsi in self.db:
            if self.db[valsi].definition:
                irc.reply(self.db[valsi].definition.encode('utf-8'))
            else:
                irc.reply("no definition")
        else:
            irc.reply('no entry')
    definition = wrap(definition, ['text'])

    def notes(self, irc, msg, args, valsi):
        """<entry>

        Get the notes for an entry.
        """
        if valsi in self.db:
            if self.db[valsi].notes:
                irc.reply(self.db[valsi].notes.encode('utf-8'))
            else:
                irc.reply("no notes")
        else:
            irc.reply('no entry')
    notes = wrap(notes, ['text'])

    def gloss(self, irc, msg, args, valsi):
        """<entry>

        Get the gloss words for an entry.
        """
        if valsi in self.db:
            places = self.db[valsi].places
            if 1 in places:
                irc.reply(', '.join([i[0] for i in places[1]]).encode('utf-8'))
            else:
                irc.reply("no glosses")
        else:
            irc.reply('no entry')
    gloss = wrap(gloss, ['text'])

    def type(self, irc, msg, args, valsi):
        """<entry>

        Get the word type of an entry.
        """
        if valsi in self.db:
            irc.reply(self.db[valsi].type)
        else:
            irc.reply('no entry')
    type = wrap(type, ['text'])

    def find(self, irc, msg, args, opts, query):
        """[--{type,selmaho,definition,notes,gloss} <value>] [--{rafsi,valsi} <commalist>] [--shuffle] [--limit <value>] [--regexp] [--like <word>] [query]

        Search for entries in jbovlaste.
        """
        type = selmaho = definition = notes = gloss = like = None
        rafsi = valsi = []
        shuffle = False
        limit = 0
        regexp = False
        for (key, val) in opts:
            if key == 'type':
                type = val
            elif key == 'rafsi':
                rafsi = []
                [rafsi.extend(i.split()) for i in val]
            elif key == 'selmaho':
                selmaho = val
            elif key == 'definition':
                definition = val
            elif key == 'notes':
                notes = val
            elif key == 'gloss':
                gloss = val
            elif key == 'valsi':
                valsi = []
                [valsi.extend(i.split()) for i in val]
            elif key == 'shuffle':
                shuffle = val
            elif key == 'limit':
                limit = val
            elif key == 'regexp':
                regexp = val
            elif key == 'like':
                like = val
        results = self.db.query(type=type, rafsi=rafsi, selmaho=selmaho,
                                definition=definition, notes=notes,
                                gloss=gloss, valsi=valsi, regexp=regexp,
                                like=like, query=query)
        if shuffle:
            random.shuffle(results)
        if irc.nested:
            if results:
                if limit == 0:
                    limit = 1
                irc.reply(' '.join(results[0:limit]))
            else:
                irc.reply('--no-results')
        else:
            if results and limit:
                results = results[0:limit]
            if results:
                rep = '; '.join([unicode(self.db[i]) for i in results])
                plural = 'entries'
                if len(results) == 1:
                    plural = 'entry'
                irc.reply('%d %s: %s' % (len(results),
                                         plural,
                                         rep.encode('utf-8')))
            else:
                irc.reply('no entries')
    find = wrap(find, [getopts({'type': 'text', 'rafsi': commalist('text'),
                                'selmaho': 'text', 'definition': 'text',
                                'notes': 'text', 'gloss': 'text',
                                'valsi': commalist('text'), 'shuffle': '',
                                'limit': 'positiveInt', 'regexp': '',
                                'like': 'text'}),
                       optional('text')])

    def show(self, irc, msg, args, opts, entries):
        """<entry> [entry...]

        Display up to five jbovlaste entries.
        """
        if not entries or ('no-results', True) in opts:
            irc.reply('no results')
        else:
            for valsi in entries.split()[0:5]:
                if valsi in self.db:
                    entry = self.db[valsi]
                    res = '%s {%s}' % (entry.type, valsi)
                    if 1 in entry.places:
                        glo = ['"%s"' % i[0] for i in entry.places[1]]
                        res = '%s glossing to %s' % (res, ', '.join(glo))
                    if entry.selmaho:
                        res = "%s of selma'o %s" % (res, entry.selmaho)
                    if entry.rafsi:
                        afx = ', '.join(map(lambda a: '-%s-' % a,
                                            entry.rafsi))
                        res = '%s with rafsi %s' % (res, afx)
                    if entry.definition:
                        res = '%s   %s' % (res, entry.definition)
                    if entry.notes:
                        res = '%s   Notes: %s' % (res, entry.notes)
                    irc.reply(res.encode('utf-8'))
                else:
                    irc.reply('no entry for {%s}' % valsi)
    show = wrap(show, [getopts({'no-results': ''}), optional('text')])


Class = Jbovlaste


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
