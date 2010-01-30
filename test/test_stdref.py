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
from vfilter import BookMatcher
from vfilter import PVerse
from vfilter import PVerseSpan
from vfilter import PPassage

from stdref import PassageFormatter
from stdref import match
from stdref import search

from testbible import bibledef
from testbible import build_bibleinfo

BIBLEINFO = build_bibleinfo()

with open('books.txt') as f:
    MATCHER = BookMatcher.fromfile(f)

with open('books.txt') as f:
    formatter = PassageFormatter.fromfile(f)

class TestBookFilter(unittest.TestCase):
    def test_match(self):
        t = match('Genesis 4:12', MATCHER, BIBLEINFO)
        v = PVerse(0, 4, 12)
        self.assertEquals(t.value, PPassage([PVerseSpan(v, v)]))

    def test_search(self):
        string = "Glory, I'm back home Genesis 16:32 - Genesis 3\n in Exodus 1:10 - Exodus 1:5 Canada"
        tokens = list(search(string, MATCHER, BIBLEINFO))

        self.assertEquals(len(tokens), 2)
        self.assertEquals(tokens[0].value, PPassage([PVerseSpan(PVerse(0, 3, 1), PVerse(0, 16, 16))]))
        self.assertEquals(tokens[1].value, PPassage([PVerseSpan(PVerse(1, 1, 5), PVerse(1, 1, 10))]))

def example_usage():
    string = "Glory, I'm back home Genesis 16:32 - Genesis 3\n in Exodus 1:10 - Exodus 1:5 Canada"
    print string
    print 32*'v'
    tokens = list(search(string, MATCHER, BIBLEINFO))

    for t in tokens:
        print t.row, t.col, string[t.start:t.end], '=>', formatter.format(t.value)


if __name__ == '__main__':
    unittest.main()

