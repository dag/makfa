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
import random


class Damerau():

    def __init__(self, like, lst):
        self.distances = {}
        for item in lst:
            self.distances[item] = self.distance(like, item)

    def cmp(self, s1, s2):
        d1 = self.distances[s1]
        d2 = self.distances[s2]
        if d1 > d2:
            return 1
        elif d1 == d2:
            return 0
        else:
            return -1

    # http://mwh.geek.nz/2009/04/26/python-damerau-levenshtein-distance/
    def distance(self, seq1, seq2):
        oneago = None
        thisrow = range(1, len(seq2) + 1) + [0]
        for x in xrange(len(seq1)):
            twoago, oneago, thisrow = oneago, thisrow, [0] * len(seq2) + [x + 1]
            for y in xrange(len(seq2)):
                delcost = oneago[y] + 1
                addcost = thisrow[y - 1] + 1
                subcost = oneago[y - 1] + (seq1[x] != seq2[y])
                thisrow[y] = min(delcost, addcost, subcost)
                if (x > 0 and y > 0 and seq1[x] == seq2[y-1]
                    and seq1[x-1] == seq2[y] and seq1[x] != seq2[y]):
                    thisrow[y] = min(thisrow[y], twoago[y-2] + 1)
        return thisrow[len(seq2) - 1]


class VlaSte():

    def __init__(self):
        def prettyplace(defn):
            def f(m):
                res = m.group(1).replace('_', '')
                return res.replace('{', '').replace('}', '')
            return re.sub(r'\$(.+?)\$', f, defn)
        self.tree = {}
        self.words = []
        tree = etree.parse(path.dirname(path.abspath(__file__)) +
                           "/xml-export.html")
        def save(valsi):
            word = valsi.get('word')
            self.words.append(word)
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
        for valsi in tree.findall('//valsi[@type="gismu"]'): save(valsi)
        for valsi in tree.findall('//valsi[@type="cmavo"]'): save(valsi)
        for valsi in tree.findall('//valsi[@type="cmavo cluster"]'):
            save(valsi)
        for valsi in tree.findall('//valsi[@type="lujvo"]'): save(valsi)
        for valsi in tree.findall('//valsi[@type="fu\'ivla"]'): save(valsi)
        for valsi in tree.findall('//valsi[@type="experimental gismu"]'):
            save(valsi)
        for valsi in tree.findall('//valsi[@type="experimental cmavo"]'):
            save(valsi)
        for valsi in tree.findall('//valsi[@type="cmene"]'): save(valsi)
        for valsi in tree.findall('//nlword'):
            word = valsi.get('valsi')
            place = valsi.get('place')
            if place == '1' or place == None:
                self.tree[word]['glosses'].append(valsi.get('word'))

    def find_type(self, inlist, type, regexp):
        if not type: return inlist
        outlist = []
        for word in inlist:
            data = self.tree[word]['type']
            if regexp and re.search(type, data, re.IGNORECASE) or \
               type.upper() == data.upper():
                outlist.append(word)
        return outlist

    def find_valsi(self, inlist, valsi, regexp):
        if not valsi: return inlist
        outlist = []
        if regexp:
            for item in valsi:
                for word in inlist:
                    if re.search(item, word, re.IGNORECASE):
                        outlist.append(word)
        else:
            for words in [i.split() for i in valsi]:
                for word in words:
                    if word in inlist:
                        outlist.append(word)
        return outlist

    def find_gloss(self, inlist, gloss, regexp):
        if not gloss: return inlist
        outlist = []
        if regexp:
            for word in inlist:
                for item in self.tree[word]['glosses']:
                    if re.search(gloss, item, re.IGNORECASE):
                        outlist.append(word)
                        break
        else:
            for word in inlist:
                glosses = self.tree[word]['glosses']
                lowered = [item.lower() for item in glosses]
                if gloss.lower() in lowered:
                    outlist.append(word)
        return outlist

    def find_rafsi(self, inlist, rafsi, regexp):
        if not rafsi: return inlist
        outlist = []
        if regexp:
            for item in rafsi:
                for word in inlist:
                    added = False
                    for raf in self.tree[word]['rafsi']:
                        if re.search(item, raf, re.IGNORECASE):
                            added = True
                            outlist.append(word)
                            break
                    if added:
                        continue
        else:
            for items in [i.split() for i in rafsi]:
                for item in items:
                    for word in inlist:
                        if item in self.tree[word]['rafsi']:
                            outlist.append(word)
                            break
        return outlist

    def find_selmaho(self, inlist, selmaho, regexp):
        if not selmaho: return inlist
        outlist = []
        for word in inlist:
            data = self.tree[word]['selmaho']
            if regexp and re.search(selmaho, data, re.IGNORECASE) or \
               selmaho.upper() == data.upper():
                outlist.append(word)
        return outlist

    def find_definition(self, inlist, definition):
        if not definition: return inlist
        outlist = []
        for word in inlist:
            data = self.tree[word]
            if re.search(definition, data['definition'], re.IGNORECASE):
                outlist.append(word)
        return outlist

    def find_notes(self, inlist, notes):
        if not notes: return inlist
        outlist = []
        for word in inlist:
            data = self.tree[word]
            if re.search(notes, data['notes'], re.IGNORECASE):
                outlist.append(word)
        return outlist

    def find(self, type=None, valsi=[], gloss=None, rafsi=[],
              selmaho=None, definition=None, notes=None, regexp=False):
        results = self.words
        results = self.find_type(results, type, regexp)
        results = self.find_valsi(results, valsi, regexp)
        results = self.find_gloss(results, gloss, regexp)
        results = self.find_rafsi(results, rafsi, regexp)
        results = self.find_selmaho(results, selmaho, regexp)
        results = self.find_definition(results, definition)
        results = self.find_notes(results, notes)
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
            elif key == 'shuffle':
                shuffle = val
            elif key == 'limit':
                limit = val
            elif key == 'regexp':
                regexp = val
            elif key == 'like':
                like = val
        results = []
        if query != None:
            results.extend(self.vlaste.find(type=type, rafsi=rafsi,
                                            selmaho=selmaho,
                                            definition=definition, notes=notes,
                                            gloss=query, valsi=valsi,
                                            regexp=regexp))
            results.extend(self.vlaste.find(type=type, rafsi=rafsi,
                                            selmaho=selmaho,
                                            definition=definition, notes=notes,
                                            gloss=gloss, valsi=[query],
                                            regexp=regexp))
            results.extend(self.vlaste.find(type=type, rafsi=[query],
                                            selmaho=selmaho,
                                            definition=definition, notes=notes,
                                            gloss=gloss, valsi=valsi,
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
            dupes = results
            results = []
            [results.append(i) for i in dupes if not results.count(i)]
        else:
            results = self.vlaste.find(type=type, rafsi=rafsi, selmaho=selmaho,
                                       definition=definition, notes=notes,
                                       gloss=gloss, valsi=valsi, regexp=regexp)
        if shuffle:
            random.shuffle(results)
        if like:
            results.sort(Damerau(like, results).cmp)
        if irc.nested:
            if len(results) > 0:
                if limit == 0:
                    limit = 1
                irc.reply(' '.join(results[0:limit]))
            else:
                irc.reply('--no-results')
        else:
            rep = []
            if results and limit > 0:
                results = results[0:limit]
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
        if entries == None or ('no-results', True) in opts:
            irc.reply('no results')
        else:
            for valsi in entries.split()[0:5]:
                if valsi in self.vlaste.tree:
                    entry = self.vlaste.tree[valsi]
                    res = '%s {%s}' % (entry['type'], valsi)
                    if len(entry['glosses']) > 0:
                        glo = ', '.join(map(lambda a: '"%s"' % a,
                                            entry['glosses']))
                        res = '%s glossing to %s' % (res, glo)
                    if entry['selmaho'] != '':
                        res = "%s of selma'o %s" % (res, entry['selmaho'])
                    if len(entry['rafsi']) > 0:
                        afx = ', '.join(map(lambda a: '-%s-' % a,
                                            entry['rafsi']))
                        res = '%s with rafsi %s' % (res, afx)
                    if entry['definition'] != '':
                        res = '%s   %s' % (res, entry['definition'])
                    if entry['notes'] != '':
                        res = '%s   Notes: %s' % (res, entry['notes'])
                    irc.reply(res.encode('utf-8'))
                else:
                    irc.reply('no entry for {%s}' % valsi)
    show = wrap(show, [getopts({'no-results': ''}), optional('text')])


Class = Jbovlaste


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
