# Copyright (c) 2010 Keegan Callin
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# * The names of individual contributors may not be used to endorse or promote
#   products derived from this software without specific prior written
#   permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import string
from warnings import warn
from itertools import chain

class Token(object):
    NUMBER = 'number'
    WORD = 'word'
    SYMBOL = 'symbol'
    WHITESPACE = 'whitespace'

    def __init__(self, type, value, start, end, row, col):
        '''
        @param days:  maximum number of days in each step.

        @type start: int
        @type end: int
        @type row: int
        @type col: int
        '''
        self._type = type
        self._value = value

        self._start = start
        self._end = end

        self._row = row
        self._col = col

    @property
    def type(self):
        return self._type

    @property
    def value(self):
        '''Value that represents token.'''
        return self._value

    @property
    def ofs(self):
        '''Deprecated.'''
        warn('Use self.start property instead.', DeprecationWarning, stacklevel=2)
        return self._start

    @property
    def start(self):
        '''Character offset at which token begins.'''
        return self._start

    @property
    def end(self):
        return self._end

    @property
    def row(self):
        '''Row at which the first character of token begins.'''
        return self._row

    @property
    def col(self):
        '''Column at which first character of token lays.'''
        return self._col

    def __str__(self):
        '''Returns str(self.value)'''
        return str(self.value)

    def __eq__(t1, t2):
        return t1.type == t2.type and \
            t1.value == t2.value and \
            t1.start == t2.start and \
            t1.end == t2.end and \
            t1.row ==t2.row and \
            t1.col == t2.col

    _REPR_TYPE = {
        NUMBER : 'Token.NUMBER',
        WORD : 'Token.WORD',
        SYMBOL : 'Token.SYMBOL',
        WHITESPACE : 'Token.WHITESPACE',
    }
    def __repr__(self):
        try:
            repr_type = type(self)._REPR_TYPE[self.type]
        except KeyError:
            repr_type = repr(self.type)
        return "Token({0}, {1}, {2}, {3}, {4}, {5}, {6})".format(repr_type, repr(self.value), repr(self.start), repr(self.end), repr(self.row), repr(self.col), repr(self.leaves))


def _chartype(char):
    if char in string.letters:
        return Token.WORD
    elif char in string.digits:
        return Token.NUMBER
    elif char in string.whitespace:
        return Token.WHITESPACE
    else:
        return Token.SYMBOL


class Tokenizer(object):
    def __init__(self, char_iterable):
        '''
        @param char_iterable: an iterable that yields chars.
        '''

        self._iter = iter(char_iterable)

        self._start = 0
        self._row = 1
        self._col = 1

    def __iter__(self):
        return self

    def next(self):
        token = None

        ofs = self._start
        row = self._row
        col = self._col

        fifo = []
        fifo_ttype = None

        while not token:
            try:
                char = self._iter.next()
                ttype = _chartype(char) # *T*oken Type

                pushback = False

                if fifo_ttype is None:
                    if ttype == Token.SYMBOL:
                        # Token.SYMBOL chars are not accumulated
                        # return immediatly.
                        token = Token(Token.SYMBOL, char, self._start, self._start + len(char), self._row, self._col)
                    else:
                        fifo_ttype = ttype
                        fifo.append(char)
                elif ttype == fifo_ttype:
                    # Continue present token
                    fifo.append(char)
                else:
                    # A new token has begun.  Return old token.
                    value = ''.join(fifo)
                    token = Token(fifo_ttype, value, self._start, self._start + len(value), self._row, self._col)

                    # push current token back into iterator
                    pushback = True

                if pushback:
                    self._iter = chain([char], self._iter)
                else:
                    # Update offset, row, col for next token
                    ofs += 1
                    if char == '\n':
                        row += 1
                        col = 1
                    else:
                        col += 1

            except StopIteration, e:
                if fifo_ttype is None:
                    raise StopIteration()
                else:
                    # return buffered token
                    value = ''.join(fifo)
                    token = Token(fifo_ttype, value, self._start, self._start + len(value), self._row, self._col)

        self._start = ofs
        self._row = row
        self._col = col

        return token


class WhitespaceFilter(object):
    def __init__(self, token_iterable):
        self._it = iter(token_iterable)

    def __iter__(self):
        return self

    def next(self):
        while True:
            token = self._it.next()
            if token.type != Token.WHITESPACE:
                return token



