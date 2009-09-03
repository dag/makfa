from subprocess import Popen, PIPE
from string import rstrip


class Camxes():
    """Communicate with the camxes program.

    >>> camxes = Camxes()
    >>> camxes.parse('coi ro do')
    'coi ro do'
    >>> camxes.parse('coi ro don')
    'coi ro'
    >>> camxes.grammatical('coi ro do')
    True
    >>> camxes.grammatical('coi ro don')
    False
    """

    def __init__(self, path='camxes'):
        self.path = path
        self._boot()

    def _boot(self):
        self._pipe = Popen([self.path, '-t'], stdin=PIPE, stdout=PIPE)
        self._pipe.stdout.readline()

    def parse(self, text):
        """Parse text and return grammatical portion."""
        text = text + '\n'
        if self._pipe.poll():
            self._boot()
        self._pipe.stdin.write(text)
        return rstrip(self._pipe.stdout.readline())

    def grammatical(self, text):
        """Check if text is grammatical."""
        return text == self.parse(text)


if __name__ == "__main__":
    import doctest
    doctest.testmod()

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
