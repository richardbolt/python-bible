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
from stdref import BibleModel

from testbible import bibledef
from testbible import build_bibleinfo

BIBLEINFO = build_bibleinfo()

f = open('books.txt')
MATCHER = BookMatcher.fromfile(f)
f.close()

f = open('books.txt')
FORMATTER = PassageFormatter.fromfile(f)
f.close()

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


class TestBibleModel(unittest.TestCase):
    def setUp(self):
        self.model = BibleModel()

    def test_books(self):
        for b in self.model.books:
            print b

    def test_bibleinfo(self):
        self.assertTrue(self.model.bibleinfo)


    def test_formatter(self):
        self.assertTrue(self.model.formatter)


    def test_match(self):
        t = self.model.match('Genesis 4:12')
        v = PVerse(0, 4, 12)
        self.assertEquals(t.value, PPassage([PVerseSpan(v, v)]))


    def test_search(self):
        string = "Glory, I'm back home Genesis 16:32 - Genesis 3\n in Exodus 1:10 - Exodus 1:5 Canada"
        tokens = list(self.model.search(string))

        self.assertEquals(len(tokens), 2)
        self.assertEquals(tokens[0].value, PPassage([PVerseSpan(PVerse(0, 3, 1), PVerse(0, 16, 16))]))
        self.assertEquals(tokens[1].value, PPassage([PVerseSpan(PVerse(1, 1, 5), PVerse(1, 1, 10))]))


    def test_format(self):
        v = PVerse(0, 4, 12)
        self.assertEquals(self.model.format(v), 'Genesis 4:12')

        p = PPassage([PVerseSpan(PVerse(0, 3, 1), PVerse(0, 16, 16))])
        self.assertEquals(self.model.format(p), 'Genesis 3:1 - 16:16')


    def test_passage(self):
        p = self.model.Passage('Gen 5:12 - Gen 1:1')
        self.assertEquals(str(p), 'Genesis 1:1 - 5:12')

        p = self.model.Passage((self.model.Span('Gen - Exo'), self.model.Span('Exo - Lev')))
        self.assertEquals(str(p), 'Genesis - Leviticus')


    def test_span(self):
        s = self.model.Span('Genesis 1:1')
        self.assertEquals(str(s), 'Genesis 1:1')

        s = self.model.Span('Genesis 1:1-10')
        self.assertEquals(str(s), 'Genesis 1:1 - 10')

        s = self.model.Span(self.model.Verse(1,1,1), self.model.Verse(1, 2, 10))
        self.assertEquals(str(s), 'Exodus 1:1 - 2:10')

        self.assertRaises(TypeError, self.model.Span, 'Ex', 5)
        self.assertRaises(TypeError, self.model.Span, 'Ex', 'ex')
        self.assertRaises(ValueError, self.model.Span, 'Easdfasdfx')


    def test_verse(self):
        v = self.model.Verse(0, 1, 1)
        self.assertEquals(str(v), 'Genesis 1:1')

        v = self.model.Verse('Gen 5:12')
        self.assertEquals(str(v), 'Genesis 5:12')

        v = self.model.Verse('Gen', 5, 12)
        self.assertEquals(str(v), 'Genesis 5:12')

        self.assertRaises(TypeError, self.model.Verse, 0)
        self.assertRaises(TypeError, self.model.Verse, 0, 0)
        self.assertRaises(ValueError, self.model.Verse, 'hello')
        self.assertRaises(TypeError, self.model.Verse, 'hello', 0)
        self.assertRaises(ValueError, self.model.Verse, 'hello', 0, 0)


if __name__ == '__main__':
    unittest.main()

