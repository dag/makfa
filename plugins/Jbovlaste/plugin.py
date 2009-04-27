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


class VlaSte():

    def __init__(self):
        def prettyplace(defn):
            defn = re.sub(r'\$x_\{?(\d+)\}?\$', r'x\1', defn)
            defn = re.sub(r'\$.+?\$', 'x$', defn)
            x = 0
            for c in range(0, len(defn)):
                if defn[c] == '$':
                    x = x + 1
                    defn = defn.replace('$', str(x), 1)
            return defn
        self.tree = {}
        tree = etree.parse(path.dirname(path.abspath(__file__)) +
                           "/xml-export.html")
        for valsi in tree.findall('//valsi'):
            word = valsi.get('word')
            self.tree[word] = {'type': valsi.get('type'),
                               'rafsi': [],
                               'selmaho': '',
                               'definition': '',
                               'notes': '',
                               'glosses': []}
            for child in valsi.getchildren():
                if child.tag == 'rafsi':
                    self.tree[word]['rafsi'].append(child.text)
                elif child.tag == 'selmaho':
                    self.tree[word]['selmaho'] = child.text
                elif child.tag == 'definition':
                    self.tree[word]['definition'] = prettyplace(child.text)
                elif child.tag == 'notes':
                    self.tree[word]['notes'] = prettyplace(child.text)
        for valsi in tree.findall('//nlword'):
            word = valsi.get('valsi')
            place = valsi.get('place')
            if place == '1' or place == None:
                self.tree[word]['glosses'].append(valsi.get('word'))

    def find(self, type=None, rafsi=None, selmaho=None, definition=None,
             notes=None, gloss=None, valsi=None, regexp=False):
        results = []
        for word, data in self.tree.iteritems():
            candidate = False
            if regexp == False:
                if type != None:
                    candidate = type == data['type']
                    if candidate == False:
                        continue
                if rafsi != None:
                    candidate = rafsi in data['rafsi']
                    if candidate == False:
                        continue
                if selmaho != None:
                    candidate = selmaho.upper() == data['selmaho'].upper()
                    if candidate == False:
                        continue
                if gloss != None:
                    candidate = gloss in data['glosses']
                    if candidate == False:
                        continue
                if valsi != None:
                    candidate = valsi == word
                    if candidate == False:
                        continue
            else:
                if type != None:
                    candidate = re.search(type, data['type']) != None
                    if candidate == False:
                        continue
                if rafsi != None:
                    candidate = False
                    for a in data['rafsi']:
                        if re.search(rafsi, a) != None:
                            candidate = True
                            break
                    if candidate == False:
                        continue
                if selmaho != None:
                    candidate = re.search(selmaho, data['selmaho'],
                                          re.IGNORECASE) != None
                    if candidate == False:
                        continue
                if gloss != None:
                    for g in data['glosses']:
                        if re.search(gloss, g) != None:
                            candidate = True
                            break
                    if candidate == False:
                        continue
                if valsi != None:
                    candidate = re.search(valsi, word, re.IGNORECASE) != None
                    if candidate == False:
                        continue
            if definition != None:
                candidate = re.search(definition, data['definition'],
                                      re.IGNORECASE) != None
                if candidate == False:
                    continue
            if notes != None:
                candidate = re.search(notes, data['notes'],
                                      re.IGNORECASE) != None
                if candidate == False:
                    continue
            if candidate == True:
                results.append(word)
        return results


class Jbovlaste(callbacks.Plugin):
    """Add the help for "@plugin help Jbovlaste" here
    This should describe *how* to use this plugin."""

    def __init__(self, irc):
        self.__parent = super(Jbovlaste, self)
        self.__parent.__init__(irc)
        self.vlaste = VlaSte()

    def selmaho(self, irc, msg, args, valsi):
        """<entry>

        Get the selma'o of a cmavo or cmavo cluster.
        """
        if valsi in self.vlaste.tree:
            if self.vlaste.tree[valsi]['selmaho'] != '':
                irc.reply(self.vlaste.tree[valsi]['selmaho'])
            else:
                irc.reply("no selma'o")
        else:
            irc.reply('no entry')
    selmaho = wrap(selmaho, ['text'])

    def rafsi(self, irc, msg, args, valsi):
        """<word>

        Get the rafsi of a word.
        """
        if valsi in self.vlaste.tree:
            lst = self.vlaste.tree[valsi]['rafsi']
            if len(lst) > 0:
                irc.reply(', '.join(lst))
            else:
                irc.reply("no rafsi")
        else:
            irc.reply('no entry')
    rafsi = wrap(rafsi, ['text'])

    def definition(self, irc, msg, args, valsi):
        """<entry>

        Get the definition for an entry.
        """
        if valsi in self.vlaste.tree:
            defn = self.vlaste.tree[valsi]['definition']
            if defn != '':
                irc.reply(defn.encode('utf-8'))
            else:
                irc.reply("no definition")
        else:
            irc.reply('no entry')
    definition = wrap(definition, ['text'])

    def notes(self, irc, msg, args, valsi):
        """<entry>

        Get the notes for an entry.
        """
        if valsi in self.vlaste.tree:
            notes = self.vlaste.tree[valsi]['notes']
            if notes != '':
                irc.reply(notes.encode('utf-8'))
            else:
                irc.reply("no notes")
        else:
            irc.reply('no entry')
    notes = wrap(notes, ['text'])

    def gloss(self, irc, msg, args, valsi):
        """<entry>

        Get the gloss words for an entry.
        """
        if valsi in self.vlaste.tree:
            lst = self.vlaste.tree[valsi]['glosses']
            if len(lst) > 0:
                irc.reply(', '.join(lst).encode('utf-8'))
            else:
                irc.reply("no glosses")
        else:
            irc.reply('no entry')
    gloss = wrap(gloss, ['text'])

    def type(self, irc, msg, args, valsi):
        """<entry>

        Get the word type of an entry.
        """
        if valsi in self.vlaste.tree:
            irc.reply(self.vlaste.tree[valsi]['type'])
        else:
            irc.reply('no entry')
    type = wrap(type, ['text'])

    def find(self, irc, msg, args, opts, query):
        """[--{type,rafsi,selmaho,definition,notes,gloss,valsi} <value>] [--regexp] [query]

        Search for entries in jbovlaste.
        """
        type = rafsi = selmaho = definition = notes = gloss = valsi = None
        regexp = False
        for (key, val) in opts:
            if key == 'type':
                type = val
            elif key == 'rafsi':
                rafsi = val
            elif key == 'selmaho':
                selmaho = val
            elif key == 'definition':
                definition = val
            elif key == 'notes':
                notes = val
            elif key == 'gloss':
                gloss = val
            elif key == 'valsi':
                valsi = val
            elif key == 'regexp':
                regexp = val
        results = []
        if query != None:
            results.extend(self.vlaste.find(type=type, rafsi=rafsi,
                                            selmaho=selmaho,
                                            definition=definition, notes=notes,
                                            gloss=query, valsi=valsi,
                                            regexp=regexp))
            results.extend(self.vlaste.find(type=type, rafsi=query,
                                            selmaho=selmaho,
                                            definition=definition, notes=notes,
                                            gloss=gloss, valsi=valsi,
                                            regexp=regexp))
            results.extend(self.vlaste.find(type=type, rafsi=rafsi,
                                            selmaho=selmaho,
                                            definition=definition, notes=notes,
                                            gloss=gloss, valsi=query,
                                            regexp=regexp))
            results.extend(self.vlaste.find(type=type, rafsi=rafsi,
                                            selmaho=query,
                                            definition=definition, notes=notes,
                                            gloss=gloss, valsi=valsi,
                                            regexp=regexp))
            results.extend(self.vlaste.find(type=type, rafsi=rafsi,
                                            selmaho=selmaho,
                                            definition=query, notes=notes,
                                            gloss=gloss, valsi=valsi,
                                            regexp=regexp))
            results.extend(self.vlaste.find(type=type, rafsi=rafsi,
                                            selmaho=selmaho,
                                            definition=definition, notes=query,
                                            gloss=gloss, valsi=valsi,
                                            regexp=regexp))
        else:
            results = self.vlaste.find(type=type, rafsi=rafsi, selmaho=selmaho,
                                       definition=definition, notes=notes, gloss=gloss,
                                       valsi=valsi, regexp=regexp)
        results = set(results)
        if irc.nested:
            irc.reply(results.pop())
        else:
            rep = []
            for res in results:
                add = '{%s}' % res
                glo = ', '.join(map(lambda g: '"%s"' % g,
                                self.vlaste.tree[res]['glosses']))
                if len(glo) > 0:
                    glo = ' %s' % glo
                rep.append('%s%s' % (add, glo))
            if len(rep) > 0:
                plural = 'entries'
                if len(rep) == 1:
                    plural = 'entry'
                joind = '; '.join(rep).encode('utf-8')
                irc.reply('%d %s: %s' % (len(rep), plural, joind))
            else:
                irc.reply('no entries')
    find = wrap(find, [getopts({'type': 'text', 'rafsi': 'text',
                                'selmaho': 'text', 'definition': 'text',
                                'notes': 'text', 'gloss': 'text',
                                'valsi': 'text', 'regexp': ''}),
                       optional('text')])

    def show(self, irc, msg, args, valsi):
        """<entry>

        Display a jbovlaste entry.
        """
        if valsi == None:
            irc.reply('no results')
        elif valsi in self.vlaste.tree:
            entry = self.vlaste.tree[valsi]
            res = '%s {%s}' % (entry['type'], valsi)
            if len(entry['glosses']) > 0:
                glo = ', '.join(map(lambda a: '"%s"' % a, entry['glosses']))
                res = '%s glossing to %s' % (res, glo)
            if entry['selmaho'] != '':
                res = "%s of selma'o %s" % (res, entry['selmaho'])
            if len(entry['rafsi']) > 0:
                afx = ', '.join(map(lambda a: '-%s-' % a, entry['rafsi']))
                res = '%s with rafsi %s' % (res, afx)
            if entry['definition'] != '':
                res = '%s   %s' % (res, entry['definition'])
            if entry['notes'] != '':
                res = '%s   Notes: %s' % (res, entry['notes'])
            irc.reply(res.encode('utf-8'))
        else:
            irc.reply('no entry')
    show = wrap(show, [optional('text')])


Class = Jbovlaste


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
