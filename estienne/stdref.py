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

from itertools import chain

from tokenizer import Tokenizer
from tokenizer import WhitespaceFilter
from vfilter import BookFilter
from vfilter import BookMatcher
from vfilter import BookFilter
from vfilter import PPassageFilter
from vfilter import PPassageRectifier
from vfilter import VFilterToken
from vfilter import _fusespanlist


class BibleRef(object):
    def __init__(self, model):
        self._model = model

    @property
    def model(self):
        return self._model

    def __str__(self):
        return self.model.formatter.format(self)

    def __repr__(self):
        return str(self)


class Passage(BibleRef):
    def __init__(self, spans, model):
        BibleRef.__init__(self, model)
        self._spans = tuple(VerseSpan(s.first, s.last, model) for s in spans)

    @property
    def spans(self):
        return self._spans


    def __iter__(self):
        return iter(self.spans)


class VerseSpan(BibleRef):
    def __calc_len(self):
        return 5
        #for book in xrange(self._first.book, self._last.book + 1):


    def __init__(self, first, last, model):
        BibleRef.__init__(self, model)
        self._first = first
        self._last = last
        self.__len = self.__calc_len()

    @property
    def first(self):
        return self._first

    @property
    def last(self):
        return self._last

    def __iter__(self):
        return VerseSpanIt(self)

    def __len__(self):
        return self.__len


    def __eq__(self, other):
        return self._first == other._first and self._last == other._last and self.model == other.model


class Verse(BibleRef):
    def __init__(self, book_idx, chapter, verse, model):
        BibleRef.__init__(self, model)

        try:
            if verse > 0 and verse <= self.model.bibleinfo[book_idx][chapter - 1] and \
                    chapter > 0 and chapter <= len(self.model.bibleinfo[book_idx]):
                self._book = book_idx
                self._chapter = chapter
                self._verse = verse
            else:
                raise IndexError()
        except IndexError:
            raise ValueError('Verse({0}, {1}, {2}) does not exist in this bible.'.format(book_idx, chapter, verse))


    @property
    def book(self):
        return self._book

    @property
    def chapter(self):
        return self._chapter

    @property
    def verse(self):
        return self._verse


    def __lt__(self, other):
        return self.book < other.book or \
            (self.book == other.book and self.chapter < other.chapter) or \
            (self.book == other.book and self.chapter == other.chapter and self.verse < other.verse)

    def __le__(self, other):
        return self < other or self == other


    def __gt__(self, other):
        return self.book > other.book or \
            (self.book == other.book and self.chapter > other.chapter) or \
            (self.book == other.book and self.chapter == other.chapter and self.verse > other.verse)


    def __ge__(self, other):
        return self > other or self == other


    def __eq__(self, other):
        return other is not None and \
            self.book == other.book and \
            self.chapter == other.chapter and \
            self.verse == other.verse and \
            self.model == other.model


    def __ne__(self, other):
        return not self.__eq__(other)



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
        first, last = span.first, span.last

        if first.book == last.book and \
                    first.chapter == 1 and first.verse == 1 and \
                    last.chapter == len(span.model.bibleinfo[first.book]) and last.verse == span.model.bibleinfo[first.book][-1]:
            return self._lut[first.book]
        elif span.first == span.last:
            return self._format_verse(span.first)
        elif first.chapter == 1 and first.verse == 1 and \
                    last.chapter == len(span.model.bibleinfo[last.book]) and last.verse == span.model.bibleinfo[last.book][last.chapter - 1]:
            return '%s - %s' % (self._lut[first.book], self._lut[last.book])
        elif first.chapter == 1 and first.verse == 1 and last.chapter == len(span.model.bibleinfo[last.book]) and last.verse == span.model.bibleinfo[last.book][last.chapter - 1]:
            return '%s - %s' % (self._lut[first.book], self._lut[last.book])
        elif first.book == last.book and first.chapter == last.chapter:
            return '%s %d:%d - %d' % (self._lut[first.book], first.chapter, first.verse, last.verse)
        elif first.book == last.book:
            return '%s %d:%d - %d:%d' % (self._lut[first.book], first.chapter, first.verse, last.chapter, last.verse)
        else:
            return '%s %d:%d - %s %d:%d' % (self._lut[first.book], first.chapter, first.verse, self._lut[last.book], last.chapter, last.verse)

    def _format_verse(self, verse):
        return '%s %d:%d' % (self._lut[verse.book], verse.chapter, verse.verse)

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
            raise ValueError('String "%s" is not a valid passage.'  % string)

    return passage_token


def search(string, matcher, bibleinfo):
    it = tokenizer(string, matcher, bibleinfo)

    for t in it:
        if t.type == VFilterToken.PASSAGE:
            yield t
    else:
        raise StopIteration()


class BibleModel(object):
    def __init__(self, bibleinfo, matcher, formatter):
        self._bibleinfo = bibleinfo
        self._matcher = matcher
        self._formatter = formatter


    def Passage(self, reference_or_spans):
        if type(reference_or_spans) is str:
            t = self.match(reference_or_spans)
            fused_spans = [self.Span(self.Verse(s.first.book, s.first.chapter, s.first.verse), self.Verse(s.last.book, s.last.chapter, s.last.verse)) for s in t.value.spans]
        else:
            spans = reference_or_spans
            fused_spans = [self.Span(self.Verse(s.first.book, s.first.chapter, s.first.verse), self.Verse(s.last.book, s.last.chapter, s.last.verse)) for s in _fusespanlist(spans, self.bibleinfo)]

        return Passage(fused_spans, self)


    def Book(self, *args):
        '''
        Synopsis:
            Book(int)
            Book(str) # not presently supported
        '''

        if len(args) == 1:
            arg = args[0]
            if type(arg) is int:
                book_idx = arg
                rv = self.Span(self.Verse(book_idx, 1, 1), self.Verse(book_idx, len(self.bibleinfo[book_idx]), self.bibleinfo[book_idx][-1]))
            elif type(arg) is str:
                raise NotImplementedError('args == (str,) not presently implemented.')
            else:
                raise ValueError('Unknown argument signature {0}'.format(type(arg)))
        else:
            raise TypeError('Function takes exactly 1 argument (%s given)' % (len(args)))

        return rv


    def Chapter(self, *args):
        '''
        Synopsis:
            Book(int, int)
            Book(str) # not presently supported
        '''

        if len(args) == 2:
            book_idx, chapter = args
            if type(book_idx) is int and type(chapter) is int:
                rv = self.Span(self.Verse(book_idx, chapter, 1), self.Verse(book_idx, chapter, self.bibleinfo[book_idx][chapter - 1]))
            else:
                raise ValueError('Unknown argument signature')
        else:
            raise TypeError('Function takes exactly 2 arguments (%s given)' % (len(args)))

        return rv


    def Span(self, reference_or_first, last = None):
        if type(reference_or_first) is str:
            if last is not None:
                raise TypeError('When type(reference_or_first) is str, last must be None; Found {0}'.format(type(last)))
            t = self.match(reference_or_first)
            p = t.value

            if len(p.spans) == 1:
                first = p.spans[0].first
                last = p.spans[0].last
                s = VerseSpan(self.Verse(first.book, first.chapter, first.verse), self.Verse(last.book, last.chapter, last.verse), self)
            else:
                raise ValueError('{0} has more than one span.'.format(repr(reference_or_first)))
        elif type(reference_or_first) is Verse and type(last) is Verse:
            first = reference_or_first
            s = VerseSpan(self.Verse(first.book, first.chapter, first.verse), self.Verse(last.book, last.chapter, last.verse), self)
        else:
            raise TypeError('When type(reference_or_first) is str, type(last) should be None; When type(reference_or_first) is Verse, type(last) should also be Verse.  Found instead {0}, {1}'.format(type(reference_or_first), type(last)))

        return s


    def Verse(self, *args):
        '''
        Synopsis:
        Verse(str, int, int) where str is a book
        Verse(int, int, int)
        Verse(str)
        '''
        if len(args) == 3 and type(args[0]) is int and type(args[1]) is int and type(args[2]) is int:
            book = args[0]
            chapter = args[1]
            verse = args[2]
            v = Verse(book, chapter, verse, self)
        elif len(args) == 3 and type(args[0]) is str and type(args[1]) is int and type(args[2]) is int:
            book_idx = self._matcher.match(args[0])
            chapter = args[1]
            verse = args[2]
            if book_idx is None:
                raise ValueError('%s could not be recognized as a book.' % (repr(args[0]),))
            else:
                v = Verse(book_idx, chapter, verse, self)
        elif len(args) == 1 and type(args[0]) is str:
            s = args[0]
            t = self.match(s)
            p = t.value
            if len(p.spans) == 1 and p.spans[0].first == p.spans[0].last:
                span = p.spans[0]
                v = Verse(span.first.book, span.first.chapter, span.first.verse, self)
            else:
                raise ValueError('%1 is not a verse.' % (repr(s),))
        else:
            raise TypeError('Unrecognized function signature.')

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
    def bibleinfo(self):
        return self._bibleinfo

    @property
    def formatter(self):
        return self._formatter








class VerseSpanIt(object):
    def __init__(self, span):
        self._span = span
        self._last = None

    def __iter__(self):
        return self

    def next(self):
        if self._last is None:
            self._last = self._span.first
        elif self._last <= self._span.last:
            bibleinfo = self._last.model.bibleinfo

            book = self._last.book
            chapter = self._last.chapter
            verse = self._last.verse

            if verse < bibleinfo[book][chapter - 1]:
                n = self._span.model.Verse(book, chapter, verse + 1)
            elif chapter < len(bibleinfo[book]):
                n = self._span.model.Verse(book, chapter + 1, 1)
            elif book < len(bibleinfo) - 1:
                n = self._span.model.Verse(book + 1, 1, 1)
            else:
                raise StopIteration()

            self._last = n
        else:
            raise StopIteration()

        return self._last


def verse_iter(passage_span_or_verse):
    if hasattr(passage_span_or_verse, 'spans'):
        p = passage_span_or_verse # passage
        it = chain(*[iter(s) for s in p])
    elif hasattr(passage_span_or_verse, 'first') and hasattr(passage_span_or_verse, 'last'):
        span = passage_span_or_verse # span
        it = iter(span)
    elif hasattr(passage_span_or_verse, 'book') and hasattr(passage_span_or_verse, 'chapter') and hasattr(passage_span_or_verse, 'verse'):
        v = passage_span_or_verse # verse
        it = iter((v,))
    else:
        raise Exception('Unknown type')

    return it



#~ class chapter_it(object):
    #~ def __init__(self, ref):
        #~ pass

    #~ def next(self):
        #~ pass

    #~ def __iter__(self):
        #~ pass


#~ class book_it(object):
    #~ def __init__(self, ref):
        #~ pass

    #~ def next(self):
        #~ pass

    #~ def __iter__(self):
        #~ pass
