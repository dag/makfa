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
from subprocess import Popen, PIPE
from string import rstrip
import re


class Jbofihe(callbacks.Plugin):
    """Add the help for "@plugin help Jbofihe" here
    This should describe *how* to use this plugin."""

    def jbofihe(self, irc, msg, args, text):
        """<text>
        
        Analyze text with jbofihe, falls back on cmafihe for
        ungrammatical text.
        """
        pipe = Popen(['jbofihe', '-x'], stdin=PIPE, stdout=PIPE)
        result = rstrip(pipe.communicate(text)[0])
        if pipe.returncode > 0:
            pipe = Popen('cmafihe', stdin=PIPE, stdout=PIPE)
            result = "not grammatical: " + rstrip(pipe.communicate(text)[0])
        irc.reply(result)
    jbofihe = wrap(jbofihe, ['text'])

    def glossy(self, irc, msg, args, text):
        """<jbofihe output>
        
        Strip jbofihe output from everything but glosses.
        """
        irc.reply(' '.join(re.findall(r'/(.+?)/\W', text)))
    glossy = wrap(glossy, ['text'])

    def cmafihe(self, irc, msg, args, text):
        """<text>
        
        Analyze text with cmafihe.
        """
        pipe = Popen('cmafihe', stdin=PIPE, stdout=PIPE)
        irc.reply(rstrip(pipe.communicate(text)[0]))
    cmafihe = wrap(cmafihe, ['text'])

    def vlatai(self, irc, msg, args, text):
        """<word> [word...]
        
        Analyze the morphology of words.
        """
        rep = []
        for words in text.split():
            pipe = Popen(['vlatai', words], stdout=PIPE)
            res = re.findall(r': (.+?) : (.+)$', pipe.communicate()[0])[0]
            if ' ' in res[1].lstrip():
                for word in res[1].split():
                    pipe = Popen(['vlatai', word], stdout=PIPE)
                    res = re.findall(r': (.+?) :', pipe.communicate()[0])[0]
                    rep.append('{%s} is a %s' % (word, res.replace('(s)', '')))
            else:
                rep.append('{%s} is a %s' % (res[1].lstrip(),
                                             res[0].replace('(s)', '')))
        irc.reply('; '.join(rep))
    vlatai = wrap(vlatai, ['text'])

    def jvocuhadju(self, irc, msg, args, words):
        """<tanru>
        
        Create lujvo from tanru.
        """
        arglist = ['jvocuhadju']
        arglist.extend(words.split())
        result = Popen(arglist, stdin=PIPE, stdout=PIPE).communicate()[0]
        lujvo = re.findall(r'^ *\d+ (.+)', result, re.MULTILINE)
        if len(lujvo) > 0:
            if irc.nested:
                irc.reply(lujvo[0])
            else:
                irc.reply(', '.join(map(lambda e: "{%s}" % e, lujvo)))
        else:
            irc.reply('no suggestions')
    jvocuhadju = wrap(jvocuhadju, ['text'])


Class = Jbofihe


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
