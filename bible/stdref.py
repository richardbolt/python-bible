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

from tokenizer import Tokenizer
from tokenizer import WhitespaceFilter
from vfilter import BookFilter
from vfilter import BookMatcher
from vfilter import BookFilter
from vfilter import PPassageFilter
from vfilter import PPassageRectifier
from vfilter import VFilterToken

from testbible import build_bibleinfo

class BibleRef(object):
    def __init__(self, bibleinfo, formatter):
        self._bibleinfo = bibleinfo
        self._formatter = formatter

    @property
    def formatter(self):
        return self._formatter

    @property
    def bibleinfo(self):
        return self._bibleinfo

    def __str__(self):
        return self.formatter.format(self)

    def __repr__(self):
        return str(self)


class Passage(BibleRef):
    def __init__(self, spans, bibleinfo, formatter):
        BibleRef.__init__(self, bibleinfo, formatter)
        self._spans = tuple(spans)

    @property
    def spans(self):
        return self._spans


class VerseSpan(BibleRef):
    def __calc_len(self):
        return 5
        #for book in xrange(self._first.book, self._last.book + 1):


    def __init__(self, first, last, bibleinfo, formatter):
        BibleRef.__init__(self, bibleinfo, formatter)
        self._first = first
        self._last = last
        self.__len = self.__calc_len()

    @property
    def first(self):
        return self._first

    @property
    def last(self):
        return self._last

    def __len__(self):
        return self.__len


class Verse(BibleRef):
    def __init__(self, book, chapter, verse, bibleinfo, formatter):
        BibleRef.__init__(self, bibleinfo, formatter)

        self._book = book
        self._chapter = chapter
        self._verse = verse


    @property
    def book(self):
        return self._book

    @property
    def chapter(self):
        return self._chapter

    @property
    def verse(self):
        return self._verse


class PassageFormatter(object):
    def __init__(self, titles):
        self._lut = {}
        for id, title in enumerate(titles):
            self._lut[id] = title

    @staticmethod
    def fromfile(f):
        titles = []

        for line in f:
            titles.append(line.split(',')[0].strip())

        return PassageFormatter(titles)

    def _format_passage(self, passage):
        span_strings = []
        for span in passage.spans:
            span_strings.append(self._format_span(span))
        return ', '.join(span_strings)

    def _format_span(self, span):
        if span.first == span.last:
            return self._format_verse(span.first)
        elif span.first.book == span.last.book and span.first.chapter == span.last.chapter:
            return '{0} {1}:{2} - {3}'.format(self._lut[span.first.book], span.first.chapter, span.first.verse, span.last.verse)
        elif span.first.book == span.last.book:
            return '{0} {1}:{2} - {3}:{4}'.format(self._lut[span.first.book], span.first.chapter, span.first.verse, span.last.chapter, span.last.verse)
        else:
            return '{0} {1}:{2} - {3} {4}:{5}'.format(self._lut[span.first.book], span.first.chapter, span.first.verse, span.last.book, span.last.chapter, span.last.verse)

    def _format_verse(self, verse):
        return '{0} {1}:{2}'.format(self._lut[verse.book], verse.chapter, verse.verse)

    def format(self, passage_span_or_verse):
        if hasattr(passage_span_or_verse, 'spans'):
            return self._format_passage(passage_span_or_verse)
        elif hasattr(passage_span_or_verse, 'first') and hasattr(passage_span_or_verse, 'last'):
            return self._format_span(passage_span_or_verse)
        elif hasattr(passage_span_or_verse, 'book') and hasattr(passage_span_or_verse, 'chapter') and hasattr(passage_span_or_verse, 'verse'):
            return self._format_verse(passage_span_or_verse)
        else:
            raise Exception('Unknown type')


def tokenizer(string, matcher, bibleinfo):
    tokenizer = Tokenizer(string)
    f0 = WhitespaceFilter(tokenizer)
    f1 = BookFilter(f0, matcher)
    f2 = PPassageFilter(f1)
    f3 = PPassageRectifier(f2, bibleinfo)

    return f3


def match(string, matcher, bibleinfo):
    it = tokenizer(string, matcher, bibleinfo)

    passage_token = None
    for t in it:
        if t.type == VFilterToken.PASSAGE:
            passage_token = t
        else:
            raise ValueError('Is not a passage token!')

    return passage_token


def search(string, matcher, bibleinfo):
    it = tokenizer(string, matcher, bibleinfo)

    for t in it:
        if t.type == VFilterToken.PASSAGE:
            yield t
    else:
        raise StopIteration()


class BibleModel(object):
    def __init__(self):
        f = open('books.txt')
        self._matcher = BookMatcher.fromfile(f)
        f.close()

        self._bibleinfo = build_bibleinfo()

        f = open('books.txt')
        self._formatter = PassageFormatter.fromfile(f)
        f.close()

    def Passage(self, reference_or_spans):
        if type(reference_or_spans) is str:
            t = self.match(reference_or_spans)
            p = Passage(t.value, self.bibleinfo, self.formatter)
        else:
            p = Passage(reference_or_spans, self.bibleinfo, self.formatter)

        return p

    def Span(self, reference_or_first, last = None):
        if type(reference_or_first) is str:
            if last is not None:
                raise TypeError('When type(reference_or_first) is str, last must be None; Found {0}'.format(type(last)))
            t = self.match(reference_or_first)
            p = t.value
            if len(p.spans) == 1:
                s = VerseSpan(p.spans[0].first, p.spans[0].last, self.bibleinfo, self.formatter)
            else:
                raise ValueError('{0} is not a span.'.format(repr(reference_or_first)))
        elif type(reference_or_first) is Verse and type(last) is Verse:
            first = reference_or_first
            s = VerseSpan(first, last, self.bibleinfo, self.formatter)
        else:
            raise TypeError('When type(reference_or_first) is str, type(last) should be None; When type(reference_or_first) is Verse, type(last) should also be Verse.  Found instead {0}, {1}'.format(type(reference_or_first), type(last)))

        return s


    def Verse(self, reference_or_book, chapter = None, verse = None):
        if type(reference_or_book) is str and chapter is None and verse is None:
            t = self.match(reference_or_book)
            p = t.value
            if len(p.spans) == 1 and p.spans[0].first == p.spans[0].last:
                v = Verse(p.spans[0].first.book, p.spans[0].first.chapter, p.spans[0].first.verse, self.bibleinfo, self.formatter)
            else:
                raise ValueError('{0} is not a verse.'.format(repr(reference_or_book)))
        elif type(reference_or_book) is int and type(chapter) is int and type(verse) is int:
            book = reference_or_book
            v = Verse(book, chapter, verse, self.bibleinfo, self.formatter)
        elif type(reference_or_book) is str and type(chapter) is int and type(verse) is int:
            book = self._matcher.match(reference_or_book)
            if book is None:
                raise ValueError('{0} could not be recognized as a book.'.format(repr(reference_or_book)))
            else:
                v = Verse(book, chapter, verse, self.bibleinfo, self.formatter)
        elif type(reference_or_book) is not str and type(reference_or_book) is not int:
            raise TypeError('type(reference_or_book) should be int or str; Found {0}'.format(type(reference_or_book)))
        elif type(reference_or_book) is str and type(chapter) is not None:
            raise TypeError('When type(reference_or_book) is str, type(chapter) should be None; Found {0}'.format(type(chapter)))
        elif type(reference_or_book) is str and type(verse) is not None:
            raise TypeError('When type(reference_or_book) is str, type(chapter) should be None; Found {0}'.format(type(chapter)))
        elif type(reference_or_book) is int and type(chapter) is not int:
            raise TypeError('When type(reference_or_book) is int, type(chapter) should be int.  Found {0}'.format(type(chapter)))
        elif type(reference_or_book) is int and type(verse) is not int:
            raise TypeError('When type(reference_or_book) is int, type(chapter) should be int.  Found {0}'.format(type(chapter)))
        else:
            assert False

        return v

    def match(self, string):
        passage = match(string, self._matcher, self._bibleinfo)
        return passage

    def search(self, string):
        for p in search(string, self._matcher, self._bibleinfo):
            yield p

    def tokens(self, string):
        for t in tokenizer(string, self._matcher, self._bibleinfo):
            yield t

    def format(self, string):
        return self.formatter.format(string)

    @property
    def books(self):
        return self._books

    @property
    def bibleinfo(self):
        return self._bibleinfo

    @property
    def formatter(self):
        return self._formatter


class verse_it(object):
    def __init__(self, ref):
        pass


    def next(self):
        pass


    def __iter__(self):
        pass


class chapter_it(object):
    def __init__(self, ref):
        pass

    def next(self):
        pass

    def __iter__(self):
        pass


class book_it(object):
    def __init__(self, ref):
        pass

    def next(self):
        pass

    def __iter__(self):
        pass
