from lxml import etree
import re
from subprocess import Popen, PIPE
from string import rstrip


_terminators = {'BE': 'BEhO',
                'PA': 'BOI',
                'BY': 'BOI',
                'COI': 'DOhU',
                'DOI': 'DOhU',
                'FIhO': 'FEhU',
                'GOI': 'GEhU',
                'NU': 'KEI',
                'KE': 'KEhE',
                'LE': 'KU',
                'LA': 'KU',
                'PEhO': 'KUhE',
                'NOI': 'KUhO',
                'LU': 'LIhU',
                'LI': 'LOhO',
                'LAhE': 'LUhU',
                'NAhE+BO': 'LUhU',
                'ME': 'MEhU',
                'NUhI': 'NUhU',
                'SEI': 'SEhU',
                'SOI': 'SEhU',
                'TO': 'TOI',
                'TUhE': 'TUhU',
                'VEI': 'VEhO'}


class Entry():

    def __init__(self, valsi, type, rafsi=[], selmaho=None,
                 definition=None, notes=None, places={}, selrafsi=[]):
        self.valsi = valsi
        self.type = type
        self.rafsi = list(rafsi)
        self.selmaho = selmaho
        self.definition = definition
        self.notes = notes
        self.places = dict(places)
        self.selrafsi = list(selrafsi)
        self._terminator = None
        self._terminates = []

    def terminator(self):
        if self._terminator:
            return self._terminator
        if self.selmaho in _terminators:
            self._terminator = _terminators[self.selmaho]
            return self._terminator

    def terminates(self):
        if self._terminates:
            return self._terminates
        self._terminates = [k for k, v in _terminators.iteritems()
                              if v == self.selmaho]
        return self._terminates

    def __str__(self):
        if 1 in self.places:
            places = [('"%s" in the sense of "%s"' % i if i[1] else
                       '"%s"' % i[0]) for i in self.places[1]]
            return '{%s} %s' % (self.valsi, ', '.join(places))
        else:
            return '{%s}' % self.valsi

    def __repr__(self):
        return '<%s>' % str(self)


class Dictionary():

    def __init__(self, file):
        self._entries = []
        self._tree = {}
        tree = etree.parse(file)
        if tree.find('//selrafsi') is None:
            self._add_selrafsi(tree, file)
        types = ['gismu', 'cmavo', 'cmavo cluster', 'lujvo', "fu'ivla",
                 'experimental gismu', 'experimental cmavo', 'cmene']
        for type in types:
            for valsi in tree.findall('//valsi[@type="%s"]' % type):
                entries = self._entries
                self._entries = []
                self._save(valsi)
                self._entries = entries + self._entries
        for valsi in tree.findall('//nlword'):
            word = valsi.get('valsi')
            place = int(valsi.get('place') or '1')
            sense = valsi.get('sense')
            if place not in self[word].places:
                self[word].places[place] = []
            self[word].places[place].append((valsi.get('word'), sense))

    def find(self, type=None, valsi=[], gloss=None, rafsi=[], like=None,
              selmaho=[], definition=None, notes=None, regexp=False):
        results = self._entries
        results = self._type(results, type, regexp)
        results = self._valsi(results, valsi, regexp)
        results = self._gloss(results, gloss, regexp)
        results = self._rafsi(results, rafsi, regexp)
        results = self._selmaho(results, selmaho, regexp)
        results = self._definition(results, definition)
        results = self._notes(results, notes)
        if like:
            results.sort(_Damerau(like, results).cmp)
        return results

    def query(self, query=None, type=None, valsi=[], gloss=None,
              rafsi=[], selmaho=[], definition=None, notes=None,
              regexp=False, like=None):
        results = []
        args = {'gloss': gloss, 'valsi': valsi, 'rafsi': rafsi,
                'selmaho': selmaho, 'definition': definition, 'like': like,
                'notes': notes, 'regexp': regexp, 'type': type}
        if query:
            listargs = ['valsi', 'rafsi', 'selmaho']
            order = ['gloss', 'valsi', 'rafsi',
                     'selmaho', 'definition', 'notes']
            for arg in order:
                copyarg = dict(args)
                if arg in listargs:
                    copyarg[arg] = [query]
                else:
                    copyarg[arg] = query
                results.extend(self.find(**copyarg))
            dupes = results
            results = []
            [results.append(i) for i in dupes if i not in results]
            if like:
                results.sort(_Damerau(like, results).cmp)
            elif not results:
                d = _Damerau(query, self._entries)
                results = [i for i in self._entries if d.distances[i] == 1]
            return results
        else:
            return self.find(**args)

    def _type(self, inlist, type, regexp):
        if not type: return inlist
        if not regexp: type = type.lower()
        return [i for i in inlist
                  if regexp and
                     re.search(type, self[i].type, re.IGNORECASE) or
                     type == self[i].type]

    def _valsi(self, inlist, valsi, regexp):
        if not valsi: return inlist
        outlist = []
        [[outlist.append(i) for i in inlist
                            if regexp and
                               re.search(v, i, re.IGNORECASE) or
                               v == i] for v in valsi]
        return outlist

    def _gloss(self, inlist, gloss, regexp):
        if not gloss: return inlist
        return [v for v in inlist
                  if any([regexp and
                          any([re.search(gloss, i, re.IGNORECASE)
                               for i in [i[0] for i in i]]) or
                          gloss in [i[0] for i in i]
                          for i in self[v].places.values()])]

    def _rafsi(self, inlist, rafsi, regexp):
        if not rafsi: return inlist
        outlist = []
        [[outlist.append(i) for i in inlist
                            if regexp and
                               any([re.search(r, a, re.IGNORECASE)
                                    for a in self[i].rafsi]) or
                               r in self[i].rafsi] for r in rafsi]
        return outlist

    def _selmaho(self, inlist, selmaho, regexp):
        if not selmaho: return inlist
        if not regexp:
            selmaho = [i.upper().replace('H', 'h') for i in selmaho]
        return [i for i in inlist 
                  if self[i].selmaho and (regexp and
                     any([re.search(s, self[i].selmaho, re.IGNORECASE)
                          for s in selmaho]) or
                     self[i].selmaho in selmaho)]

    def _definition(self, inlist, definition):
        if not definition: return inlist
        return [i for i in inlist
                  if re.search(definition, self[i].definition, re.IGNORECASE)]

    def _notes(self, inlist, notes):
        if not notes: return inlist
        return [i for i in inlist
                  if self[i].notes and
                     re.search(notes, self[i].notes, re.IGNORECASE)]

    def _prettyplace(self, defn):
        def f(m):
            res = m.group(1).replace('_', '')
            return res.replace('{', '').replace('}', '')
        return re.sub(r'\$(.+?)\$', f, defn.replace('\n', ' '))

    def _add_selrafsi(self, tree, file):
        for lujvo in tree.findall('//valsi[@type="lujvo"]'):
            word = lujvo.get('word')
            pipe = Popen(['decomp', word], stdout=PIPE)
            decomp = pipe.communicate()[0]
            if not pipe.returncode > 0:
                veljvo = rstrip(decomp).split('+')
                for selrafsi in veljvo:
                    element = etree.Element('selrafsi')
                    element.text = selrafsi
                    lujvo.append(element)
        tree.write(file)

    def _save(self, valsi):
        word = valsi.get('word')
        self._entries.append(word)
        self[word] = Entry(word, valsi.get('type'))
        for child in valsi.getchildren():
            if child.tag == 'rafsi':
                self[word].rafsi.append(child.text)
            elif child.tag == 'selmaho':
                self[word].selmaho = child.text
            elif child.tag == 'definition':
                self[word].definition = self._prettyplace(child.text)
            elif child.tag == 'notes':
                self[word].notes = self._prettyplace(child.text)
            elif child.tag == 'selrafsi':
                self[word].selrafsi.append(child.text)

    def __getitem__(self, key):
        return self._tree[key]

    def __setitem__(self, key, value):
        self._tree[key] = value

    def __iter__(self):
        return iter(self._entries)

    def __len__(self):
        return len(self._entries)


class _Damerau():

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


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
