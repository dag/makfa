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


try:
    reload(jbovlaste)
except:
    import jbovlaste


class Jbovlaste(callbacks.Plugin):
    """Add the help for "@plugin help Jbovlaste" here
    This should describe *how* to use this plugin."""

    def __init__(self, irc):
        self.__parent = super(Jbovlaste, self)
        self.__parent.__init__(irc)
        self.db = jbovlaste.Dictionary('data/jbovlaste-en.xml')

    def selmaho(self, irc, msg, args, valsi):
        """<entry> [entry...]

        List selma'o for entries.
        """
        if irc.nested:
            L = [self.db[i].selmaho for i in valsi.split()
                                    if i in self.db and self.db[i].selmaho]
            if L:
                irc.reply(' '.join(L))
        else:
            L = ['{%s} %s' % (i, self.db[i].selmaho)
                 for i in valsi.split()
                 if i in self.db and self.db[i].selmaho]
            if L:
                plural = 'entries'
                if len(L) == 1:
                    plural = 'entry'
                irc.reply('%d %s: %s' % (len(L), plural, '; '.join(L)))
            else:
                irc.reply("no selma'o")
    selmaho = wrap(selmaho, ['text'])

    def rafsi(self, irc, msg, args, valsi):
        """<word> [word...]

        List rafsi for words.
        """
        if irc.nested:
            L = [' '.join(self.db[i].rafsi)
                 for i in valsi.split() if i in self.db and self.db[i].rafsi]
            if L:
                irc.reply(' '.join(L))
        else:
            L = ['{%s} %s' % (i, ', '.join(['-%s-' % i
                                            for i in self.db[i].rafsi]))
                 for i in valsi.split() if i in self.db and self.db[i].rafsi]
            if L:
                plural = 'entries'
                if len(L) == 1:
                    plural = 'entry'
                irc.reply('%d %s: %s' % (len(L), plural, '; '.join(L)))
            else:
                irc.reply('no rafsi')
    rafsi = wrap(rafsi, ['text'])

    def definition(self, irc, msg, args, valsi):
        """<entry> [entry...]

        List definitions for entries.
        """
        valsi = valsi.split()
        if irc.nested:
            if valsi and valsi[0] in self.db:
                irc.reply(self.db[valsi[0]].definition.encode('utf-8'))
        else:
            L = ['{%s} "%s"' % (i, self.db[i].definition.encode('utf-8'))
                 for i in valsi if i in self.db]
            if L:
                plural = 'entries'
                if len(L) == 1:
                    plural = 'entry'
                irc.reply('%d %s: %s' % (len(L), plural, ';  '.join(L)))
            else:
                irc.reply('no definition')
    definition = wrap(definition, ['text'])

    def notes(self, irc, msg, args, valsi):
        """<entry> [entry...]

        List notes for entries.
        """
        valsi = valsi.split()
        if irc.nested:
            if valsi and valsi[0] in self.db:
                irc.reply(self.db[valsi[0]].notes.encode('utf-8'))
        else:
            L = ['{%s} "%s"' % (i, self.db[i].notes.encode('utf-8'))
                 for i in valsi if i in self.db and self.db[i].notes]
            if L:
                plural = 'entries'
                if len(L) == 1:
                    plural = 'entry'
                irc.reply('%d %s: %s' % (len(L), plural, ';  '.join(L)))
            else:
                irc.reply('no notes')
    notes = wrap(notes, ['text'])

    def gloss(self, irc, msg, args, valsi):
        """<entry> [entry...]

        List gloss words for entries.
        """
        valsi = valsi.split()
        if irc.nested:
            if valsi and valsi[0] in self.db and 1 in self.db[valsi[0]].places:
                irc.reply(self.db[valsi[0]].places[1][0][0])
        else:
            L = ['{%s} %s' % (i, ', '.join([('"%s" in the sense of "%s"' % g
                                             if g[1] else '"%s"' % g[0])
                                            for g in self.db[i].places[1]]))
                 for i in valsi if i in self.db and 1 in self.db[i].places]
            if L:
                plural = 'entries'
                if len(L) == 1:
                    plural = 'entry'
                irc.reply('%d %s: %s' % (len(L), plural, '; '.join(L)))
            else:
                irc.reply('no glosses')
    gloss = wrap(gloss, ['text'])

    def type(self, irc, msg, args, valsi):
        """<entry> [entry...]

        List types for entries.
        """
        if irc.nested:
            L = [self.db[i].type for i in valsi.split() if i in self.db]
            if L:
                irc.reply(' '.join(L))
        else:
            L = ['{%s} %s' % (i, self.db[i].type)
                 for i in valsi.split() if i in self.db]
            if L:
                plural = 'entries'
                if len(L) == 1:
                    plural = 'entry'
                irc.reply('%d %s: %s' % (len(L), plural, '; '.join(L)))
            else:
                irc.reply("no types")
    type = wrap(type, ['text'])

    def find(self, irc, msg, args, opts, query):
        """[--{type,definition,notes,gloss} <value>] [--{rafsi,valsi,selmaho} <commalist>] [--shuffle] [--limit <value>] [--regexp] [--like <word>] [query]

        Search for entries in jbovlaste.
        """
        type = definition = notes = gloss = like = None
        rafsi = valsi = selmaho = []
        shuffle = False
        limit = None
        regexp = False
        for (key, val) in opts:
            if key == 'type':
                type = val
            elif key == 'rafsi':
                rafsi = []
                [rafsi.extend(i.split()) for i in val]
            elif key == 'selmaho':
                selmaho = []
                [selmaho.extend(i.split()) for i in val]
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
        if not regexp:
            valsi = [i.replace('.', ' ') for i in valsi]
        results = self.db.query(type=type, rafsi=rafsi, selmaho=selmaho,
                                definition=definition, notes=notes,
                                gloss=gloss, valsi=valsi, regexp=regexp,
                                like=like, query=query)
        if shuffle:
            random.shuffle(results)
        if irc.nested:
            results = [i.replace(' ', '.') for i in results]
            if results:
                if limit is None:
                    irc.reply(' '.join(results))
                else:
                    irc.reply(' '.join(results[0:limit]))
            else:
                irc.reply('--no-results')
        else:
            if results and limit > 0:
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
                                'selmaho': commalist('text'),
                                'definition': 'text',
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
            if not irc.nested:
                irc.reply('no results')
        else:
            dupes = entries.split()
            entries = []
            [entries.append(i.replace('.', ' '))
             for i in dupes if i not in entries]
            if irc.nested:
                if entries:
                    irc.reply(' '.join(entries))
            else:
                for valsi in entries[0:5]:
                    if valsi in self.db:
                        entry = self.db[valsi]
                        res = '%s {%s}' % (entry.type, valsi)
                        if entry.selrafsi:
                            veljvo = ' '.join(entry.selrafsi)
                            res = '%s from tanru {%s}' % (res, veljvo)
                        if 1 in entry.places:
                            glo = [('"%s" in the sense of "%s"' % i if i[1] else
                                    '"%s"' % i[0]) for i in entry.places[1]]
                            res = '%s glossing to %s' % (res, ', '.join(glo))
                        if entry.selmaho:
                            res = "%s of selma'o %s" % (res, entry.selmaho)
                        if entry.terminator():
                            terminator = entry.terminator()
                            res = '%s with terminator %s' % (res, terminator)
                        if entry.terminates():
                            terminates = ', '.join(entry.terminates())
                            res = '%s terminating %s' % (res, terminates)
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
