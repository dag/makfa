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
        pipe = Popen(['jbofihe', '-x'], stdin=PIPE, stdout=PIPE)
        result = rstrip(pipe.communicate(text)[0])
        if pipe.returncode > 0:
            pipe = Popen('cmafihe', stdin=PIPE, stdout=PIPE)
            result = "not grammatical: " + rstrip(pipe.communicate(text)[0])
        irc.reply(result)
    jbofihe = wrap(jbofihe, ['text'])

    def glossy(self, irc, msg, args, text):
        irc.reply(' '.join(re.findall(r'/(.+?)/\W', text)))
    glossy = wrap(glossy, ['text'])

    def cmafihe(self, irc, msg, args, text):
        pipe = Popen('cmafihe', stdin=PIPE, stdout=PIPE)
        irc.reply(rstrip(pipe.communicate(text)[0]))
    cmafihe = wrap(cmafihe, ['text'])

    def jvocuhadju(self, irc, msg, args, words):
        arglist = ['jvocuhadju']
        arglist.extend(words.split())
        result = Popen(arglist, stdin=PIPE, stdout=PIPE).communicate()[0]
        lujvo = re.findall(r'^ *\d+ (.+)', result, re.MULTILINE)
        if len(lujvo) > 0:
            irc.reply(', '.join(map(lambda e: "{%s}" % e, lujvo)))
        else:
            irc.reply('no suggestions')
    jvocuhadju = wrap(jvocuhadju, ['text'])


Class = Jbofihe


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
