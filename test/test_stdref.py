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
from estienne.vfilter import BookMatcher
from estienne.vfilter import PVerse
from estienne.vfilter import PVerseSpan
from estienne.vfilter import PPassage

from estienne.stdref import PassageFormatter
from estienne.stdref import match
from estienne.stdref import search
from estienne.stdref import BibleModel
from estienne.stdref import verse_iter

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
        akas = (
            ('one',),
            ('two',),
            ('three',),
            ('four',),
            ('five',),
            ('six',),
        )

        matcher = BookMatcher(akas)

        titles = [aka[0] for aka in akas]

        formatter = PassageFormatter(titles)

        bibleinfo = (
            (1,),
            (1, 2),
            (1, 2, 3),
            (1, 2, 3, 4),
            (1, 2, 3, 4, 5),
            (1, 2, 3, 4, 5, 6)
        )

        self.model = BibleModel(bibleinfo, matcher, formatter)

    def test_bibleinfo(self):
        self.assertTrue(self.model.bibleinfo)


    def test_formatter(self):
        self.assertTrue(self.model.formatter)


    def test_match(self):
        t = self.model.match('five 3:2')
        v = PVerse(4, 3, 2)
        self.assertEquals(t.value, PPassage([PVerseSpan(v, v)]))


    def test_search(self):
        string = "Glory, I'm back home one 16:32 - three 3\n in four 2:1 - five 5:4 Canada"
        tokens = list(self.model.search(string))

        self.assertEquals(len(tokens), 2)
        self.assertEquals(tokens[0].value, PPassage([PVerseSpan(PVerse(0, 1, 1), PVerse(2, 3, 3))]))
        self.assertEquals(tokens[1].value, PPassage([PVerseSpan(PVerse(3, 2, 1), PVerse(4, 5, 4))]))


    def test_format(self):
        v = PVerse(0, 4, 12)
        self.assertEquals(self.model.format(v), 'one 4:12')

        p = PPassage([PVerseSpan(PVerse(0, 3, 1), PVerse(0, 16, 16))])
        self.assertEquals(self.model.format(p), 'one 3:1 - 16:16')


    def test_passage(self):
        self.assertRaises(ValueError, self.model.Passage, 'flugelhorn')

        s = 'one 1:1 - four 3:1'
        p = self.model.Passage(s)
        self.assertEquals(str(p), s)

        p = self.model.Passage('one - three, four - six')
        self.assertEquals(str(p), 'one - six')

        p = self.model.Passage((self.model.Span('one - three'), self.model.Span('four - six')))
        self.assertEquals(str(p), 'one - six')


    def test_span(self):
        self.assertRaises(ValueError, self.model.Span, 'flugelhorn')
        s = self.model.Span('one 1:1')
        self.assertEquals(str(s), 'one')

        s = self.model.Span('six 1:1-10')
        self.assertEquals(str(s), 'six 1:1')

        s = self.model.Span(self.model.Verse(1,1,1), self.model.Verse(2, 2, 2))
        self.assertEquals(str(s), 'two 1:1 - three 2:2')

        self.assertRaises(TypeError, self.model.Span, 'Ex', 5)
        self.assertRaises(TypeError, self.model.Span, 'Ex', 'ex')
        self.assertRaises(ValueError, self.model.Span, 'Easdfasdfx')


    def test_verse(self):
        v = self.model.Verse(0, 1, 1)
        self.assertEquals(str(v), 'one 1:1')

        v = self.model.Verse('two 2:6')
        self.assertEquals(str(v), 'two 2:2')

        v = self.model.Verse('three', 3, 3)
        self.assertEquals(str(v), 'three 3:3')

        self.assertRaises(TypeError, self.model.Verse, 0)
        self.assertRaises(TypeError, self.model.Verse, 0, 0)
        self.assertRaises(ValueError, self.model.Verse, 'hello')
        self.assertRaises(TypeError, self.model.Verse, 'hello', 0)
        self.assertRaises(ValueError, self.model.Verse, 'hello', 0, 0)
        self.assertRaises(ValueError, self.model.Verse, 0, 1, 0)
        self.assertRaises(ValueError, self.model.Verse, 0, 0, 1)


    def test_book(self):
        for book_idx in xrange(0, len(self.model.bibleinfo)):
            b = self.model.Book(book_idx)
            s = self.model.Span(self.model.Verse(book_idx, 1, 1), self.model.Verse(book_idx, len(self.model.bibleinfo[book_idx]), self.model.bibleinfo[book_idx][-1]))

            self.assertEquals(s, b)

        self.assertEquals(str(self.model.Book(2)), 'three')
        self.assertEquals(str(self.model.Book(0)), 'one')
        self.assertRaises(ValueError, self.model.Book, 10)


    def test_chapter(self):
        for book_idx in xrange(0, len(self.model.bibleinfo)):
            for chapter in xrange(1, len(self.model.bibleinfo[book_idx]) + 1):
                c = self.model.Chapter(book_idx, chapter)
                s = self.model.Span(self.model.Verse(book_idx, chapter, 1), self.model.Verse(book_idx, chapter, self.model.bibleinfo[book_idx][chapter-1]))

                self.assertEquals(s, c)

        self.assertRaises(ValueError, self.model.Chapter, 3, 0)


    def test_passage_verse_iter(self):
        p = self.model.Passage('one - six')
        it = verse_iter(p)

        for book in xrange(0, 6):
            for chapter in xrange(1, book + 2):
                for verse in xrange(1, chapter + 1):
                    self.assertEquals(it.next(), self.model.Verse(book, chapter, verse))
        self.assertRaises(StopIteration, it.next)


    def test_span_verse_iter(self):
        s = self.model.Span('one - six')
        it = verse_iter(s)

        for book in xrange(0, 6):
            for chapter in xrange(1, book + 2):
                for verse in xrange(1, chapter + 1):
                    self.assertEquals(it.next(), self.model.Verse(book, chapter, verse))
        self.assertRaises(StopIteration, it.next)


    def test_verse_verse_iter(self):
        v = self.model.Verse('one 1:1')
        it = verse_iter(v)

        self.assertEquals(it.next(), self.model.Verse(0, 1, 1))
        self.assertRaises(StopIteration, it.next)


if __name__ == '__main__':
    unittest.main()

