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

import unittest
from tokenizer import Token
from tokenizer import Tokenizer
from tokenizer import WhitespaceFilter

def outer_assigned():
    var_outer = False
    def tryme():
        return not var_outer
    return tryme()

class TestTokenizer(unittest.TestCase):
    def test_inner_outer(self):
        self.assertTrue(outer_assigned())

    def test_class_outer_assnt(self):
        var_outer = False
        def tryme():
            return not var_outer
        self.assertTrue(tryme())

    def test_j316(self):
        string = 'John 3:16'

        tokenizer = Tokenizer(string)
        tokens = list(tokenizer)
        self.assertEquals(len(tokens), 5)
        john, whitespace, three, colon, sixteen = tokens
        self.assertEquals(john, Token(Token.WORD, 'John', 0, 4, 1, 1))
        self.assertEquals(whitespace, Token(Token.WHITESPACE, ' ', 4, 5, 1, 5))
        self.assertEquals(three, Token(Token.NUMBER, '3', 5, 6, 1, 6))
        self.assertEquals(colon, Token(Token.SYMBOL, ':', 6, 7, 1, 7))


    def test_newline(self):
        string = 'Hello \n newlines'
        tokenizer = Tokenizer(string)
        tokens = list(tokenizer)

        self.assertEquals(len(tokens), 3)
        hello, ws, newlines = tokens
        self.assertEquals(hello, Token(Token.WORD, 'Hello', 0, 5, 1, 1))
        self.assertEquals(ws, Token(Token.WHITESPACE, ' \n ', 5, 8, 1, 6))
        self.assertEquals(newlines, Token(Token.WORD, 'newlines', 8, 16, 2, 2))


if __name__ == '__main__':
    unittest.main()
