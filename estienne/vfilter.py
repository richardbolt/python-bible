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
import os.path
from tokenizer import Token
import itertools
from collections import deque


class PVerse(object):
    def __init__(self, book, chapter, verse):
        if book is None:
            raise ValueError('book must not be None.')
        self._book = book

        if chapter is None:
            self._chapter = chapter
            if verse is not None:
                raise ValueError('When chapter is None verse must also be None.  Instead found {0}'.format(repr(verse)))
        else:
            self._chapter = int(chapter)

        if verse is None:
            self._verse = None
        else:
            self._verse = int(verse)

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

    def __repr__(self):
        return 'PVerse({0}, {1}, {2})'.format(self.book, self.chapter, self.verse)

    def __str__(self):
        return '{0} {1}:{2}'.format(self.book, self.chapter, self.verse)

    def __eq__(self, other):
        return other is not None and self.book == other.book and self.chapter == other.chapter and self.verse == other.verse

    def __ne__(self, other):
        return not self.__eq__(other)


class PVerseSpan(object):
    def __init__(self, first, last):
        self._first = first
        self._last = last

    @property
    def first(self):
        return self._first

    @property
    def last(self):
        return self._last

    def __repr__(self):
        return 'PVerseSpan({0}, {1})'.format(repr(self.first), repr(self.last))

    def __str__(self):
        return '{0} - {1}'.format(self.first, self.last)

    def __eq__(self, other):
        return self.first == other.first and self.last == other.last

    def __ne__(self, other):
        return not (self == other)


class PPassage(object):
    def __init__(self, spans):
        self._spans = tuple(spans)
        self.__str = None
        self.__repr = None

    def __iter__(self):
        return iter(self.spans)

    @property
    def spans(self):
        return self._spans

    def __repr__(self):
        return 'PPassage({0})'.format(repr(self.spans))

    def __str__(self):
        if self.__str is None:
            self.__str = ', '.join([str(span) for span in self.spans])

        return self.__str

    def __len__(self):
        return len(self.spans)

    def __eq__(self, other):
        return self.spans == other.spans


class VFilterToken(Token):
    BOOK = 'book'
    VERSE = 'verse'
    SPAN = 'span'
    PASSAGE = 'passage'

    _REPR_TYPE = {
        BOOK : 'VFilterToken.BOOK',
        VERSE : 'VFilterToken.VERSE',
        SPAN : 'VFilterToken.SPAN',
        PASSAGE : 'VFilterToken.PASSAGE',
    }
    def __repr__(self):
        try:
            repr_type = type(self)._REPR_TYPE[self.type]
        except KeyError:
            repr_type = repr(self.type)
        return "Token({0}, {1}, {2}, {3}, {4}, {5})".format(repr_type, repr(self.value), repr(self.start), repr(self.end), repr(self.row), repr(self.col))




def _booktitle_normalize(string):
    '''String normalization function used by BookMatcher.'''
    s = string.replace(' ', '')
    s = s.lower()
    s = s.strip()

    return s


class BookMatcher(object):
    def __init__(self, iterable):
        lut = {}

        for idx, akas in enumerate(iterable):
            for title in akas:
                title = _booktitle_normalize(title)
                if title:
                    if title in lut:
                        raise KeyError('Duplicate book entry for {0}'.format(repr(title)))
                    else:
                        lut[title] = idx

        self._lut = lut

    @staticmethod
    def fromfile(f):
        akas = []

        for line in f:
            akas.append(line.split(','))

        return BookMatcher(akas)

    def match(self, string):
        string = _booktitle_normalize(string)

        try:
            return self._lut[string]
        except KeyError:
            return None


class BookFilter(object):
    MAX_SIZE = 10

    def __init__(self, token_iterable, book_matcher):
        self._it = token_iterable
        self._buffer = []

        self.matcher = book_matcher


    def __iter__(self):
        return self


    def next(self):
        try:
            while len(self._buffer) < type(self).MAX_SIZE:
                self._buffer.append(self._it.next())
        except StopIteration:
            if not self._buffer:
                raise StopIteration()

        for join_len in xrange(min([len(self._buffer), type(self).MAX_SIZE]), 0, -1):
            title = ''.join([str(token.value) for token in self._buffer[0 : join_len]])
            idx = self.matcher.match(title)

            if idx is not None:
                start_token = self._buffer[0]
                end_token = self._buffer[join_len - 1]
                self._buffer = self._buffer[join_len : ]
                return VFilterToken(VFilterToken.BOOK, idx, start_token.start, end_token.end, start_token.row, start_token.col)
        else:
            return self._buffer.pop(0)




#~ class PVerseFilter(object):
    #~ def __init__(self, token_iterable):
        #~ self._it = token_iterable
        #~ self._buffer = []


#~ class PSpanFilter(object):
    #~ def __init__(self, token_iterable):
        #~ self._it = token_iterable
        #~ self._buffer = []



class PVerseFilter(object):
    def __init__(self, token_iterable):
        self._buffer = []
        self._it = token_iterable

    def __iter__(self):
        return self

    def next(self):
        return self.seeded_next(None)

    def seeded_next(self, seed):
        # (1) Book
        # (2) Book Chapter
        # (4) Book Chapter Colon Verse
        #
        # (1) | Book | Chapter
        # (1) | Book Chapter | Verse
        # (3) | Book | Chapter Colon Verse

        buffer = self._buffer
        try:
            while len(buffer) < 4:
                buffer.append(self._it.next())
        except StopIteration:
            if not buffer:
                raise

        book = None
        chapter = None
        verse = None

        if len(buffer) >= 4 and \
                buffer[0].type == VFilterToken.BOOK and buffer[1].type == Token.NUMBER and buffer[2].type == Token.SYMBOL and buffer[2].value == ':' and buffer[3].type == Token.NUMBER:
            # 4
            # Book Chapter Colon Verse
            book = buffer[0].value
            chapter = buffer[1].value
            verse = buffer[3].value
            consumed = 4
        elif len(buffer) >= 3 and \
                seed is not None and seed.book is not None and seed.chapter is not None and \
                buffer[0].type == Token.NUMBER and buffer[1].type == Token.SYMBOL and buffer[1].value == ':' and buffer[2].type == Token.NUMBER:
            # 3
            # | Book | Chapter Colon Verse
            book = seed.book
            chapter = buffer[0].value
            verse = buffer[2].value
            consumed = 3
        elif len(buffer) >= 2 and \
                buffer[0].type == VFilterToken.BOOK and buffer[1].type == Token.NUMBER:
            # 2
            # Book Chapter
            book = buffer[0].value
            chapter = buffer[1].value
            consumed = 2
        elif len(buffer) >= 1 and \
                buffer[0].type == VFilterToken.BOOK:
            # 1
            # Book
            book = buffer[0].value
            consumed = 1
        elif len(buffer) >= 1 and \
                seed is not None and seed.book is not None and seed.chapter is not None and seed.verse is not None and \
                buffer[0].type == Token.NUMBER:
            # 1
            # | Book Chapter | Verse
            book = seed.book
            chapter = seed.chapter
            verse = buffer[0].value
            consumed = 1
        elif len(buffer) >= 1 and \
                seed is not None and seed.book is not None and seed.chapter is not None and \
                buffer[0].type == Token.NUMBER:
            # 1
            # | Book | Chapter
            book = seed.book
            chapter = buffer[0].value
            consumed = 1
        else:
            consumed = 0

        if consumed:
            start = buffer[0].start
            end = buffer[consumed - 1].end
            row = buffer[0].row
            col = buffer[0].col

            self._buffer = buffer[consumed:]
            return Token(VFilterToken.VERSE, PVerse(book, chapter, verse), start, end, row, col)
        else:
            return buffer.pop(0)


class PVerseSpanFilter(object):
    def __init__(self, token_iterable):
        self._fifo = deque()
        self._it = PVerseFilter(token_iterable)

    def __iter__(self):
        return self

    def next(self):
        return self.seeded_next(None)

    def seeded_next(self, seed):
        t_start = None
        t_dash = None
        t_finish = None

        while True:
            try:
                if self._fifo:
                    t = self._fifo.popleft()
                else:
                    t = self._it.seeded_next(seed)
            except StopIteration:
                if t_dash is not None and t_finish is None:
                    self._fifo.append(t_dash)

                if t_start:
                    if t_finish is None:
                        t_finish = t_start

                    return VFilterToken(VFilterToken.SPAN,
                        PVerseSpan(t_start.value, t_finish.value),
                        t_start.start,
                        t_finish.end,
                        t_start.row,
                        t_start.col)
                else:
                    raise

            if t_start is None:
                if t.type == VFilterToken.VERSE:
                    # Genesis 1:1
                    t_start = t
                    seed = t_start.value
                else:
                    return t
            else:
                if t_dash is None:
                    if t.type == Token.SYMBOL and t.value == '-':
                        # there is a verse span
                        # Genesis 1:1 - ???
                        t_dash = t
                    else:
                        # There is no dash.  Push token into iterator
                        # return versespan with start and end verse
                        # Genesis 1:1 XXX
                        self._fifo.append(t)
                        return VFilterToken(VFilterToken.SPAN,
                            PVerseSpan(t_start.value, t_start.value),
                            t_start.start,
                            t_start.end,
                            t_start.row,
                            t_start.col)
                else:
                    if t.type == VFilterToken.VERSE:
                        t_finish = t
                        return VFilterToken(VFilterToken.SPAN,
                            PVerseSpan(t_start.value, t_finish.value),
                            t_start.start,
                            t_finish.end,
                            t_start.row,
                            t_start.col)
                    else:
                        self._fifo.append(t_dash)
                        self._fifo.append(t)
                        return VFilterToken(VFilterToken.SPAN,
                            PVerseSpan(t_start.value, t_start.value),
                            t_start.start,
                            t_start.end,
                            t_start.row,
                            t_start.col)


# Genesis
# Genesis 1
# Genesis 1, 2, 3
# Genesis 1:1, 2, 3
# Genesis 1 - 2
# Genesis 1:5 - 2:
class PPassageFilter(object):
    def __init__(self, token_iterable):
        self._it = PVerseSpanFilter(token_iterable)
        self._fifo = deque()

    def __iter__(self):
        return self

    def next(self):
        seed = None

        tokens = []
        spans = []
        t_comma = None

        while True:
            try:
                if self._fifo:
                    t = self._fifo.popleft()
                else:
                    t = self._it.seeded_next(seed)
            except StopIteration:
                if t_comma is not None:
                    self._fifo.append(t_comma)

                if spans:
                    return VFilterToken(VFilterToken.PASSAGE,
                        PPassage(spans),
                        tokens[0].start,
                        tokens[-1].end,
                        tokens[0].row,
                        tokens[0].col)
                else:
                    raise

            if t.type == VFilterToken.SPAN:
                if t_comma is not None:
                    tokens.append(t_comma)
                    t_comma = None
                tokens.append(t)
                spans.append(t.value)
                seed = t.value.last
            elif spans and t_comma is None and t.type == Token.SYMBOL and (t.value == ',' or t.value == ';'):
                t_comma = t
            else:
                # Unexpected tokens
                if spans:
                    if t_comma is not None:
                        self._fifo.append(t_comma)
                    self._fifo.append(t)

                    return VFilterToken(VFilterToken.PASSAGE,
                        PPassage(spans),
                        tokens[0].start,
                        tokens[-1].end,
                        tokens[0].row,
                        tokens[0].col)
                else:
                    return t


def _spancmp(s1, s2):
    '''Compares s1.first to s2.first.'''
    s1 = s1.first
    s2 = s2.first
    if s1.book == s2.book and s1.chapter == s2.chapter and s1.verse == s2.verse:
        return 0
    elif s1.book == s2.book and s1.chapter == s2.chapter:
        if s1.verse < s2.verse:
            return -1
        else:
            return 1
    elif s1.book == s2.book:
        if s1.chapter < s2.chapter:
            return -1
        else:
            return 1
    else:
        if s1.book < s2.book:
            return -1
        else:
            return 1


def _isnextverse(v1, bibleinfo):
    try:
        _nextverse(v1, bibleinfo)
        return True
    except ValueError:
        return False

def _nextverse(v1, bibleinfo):
    book = v1.book
    chapter = v1.chapter
    verse = v1.verse

    if verse < bibleinfo[book][chapter - 1]:
        return PVerse(book, chapter, verse + 1)
    elif chapter < len(bibleinfo[book]):
        return PVerse(book, chapter + 1, 1)
    elif book < len(bibleinfo) - 1:
        return PVerse(book + 1, 1, 1)
    else:
        raise ValueError('Last verse in bible; no succeeding verse!')


def _fusespans(s1, s2, bibleinfo):
    ERR_CANNOT_FUSE = 'Cannot fuse spans; they do not overlap.'

    if s1.first <= s2.first:
        if s1.last >= s2.first or (_isnextverse(s1.last, bibleinfo) and _nextverse(s1.last, bibleinfo) >= s2.first):
            if s1.last >= s2.last:
                new_span = s1
            else:
                new_span = PVerseSpan(s1.first, s2.last)
        else:
            raise ValueError(ERR_CANNOT_FUSE)
    else:
        if s1.first <= s2.last or (_isnextverse(s2.last, bibleinfo) and s1.first <= _nextverse(s2.last, bibleinfo)):
            if s1.last <= s2.last:
                new_span = s2
            else:
                new_span = PVerseSpan(s2.first, s1.last)
        else:
            raise ValueError(ERR_CANNOT_FUSE)

    return new_span


def _fusespanlist(spans, bibleinfo):
    fused_spans = list(spans)

    idx = 0
    while idx < len(fused_spans) - 1:
        try:
            fused_spans[idx] = _fusespans(spans[idx], spans[idx + 1], bibleinfo)
            fused_spans.pop(idx + 1)
        except ValueError:
            idx += 1

    return fused_spans


def _fix_verse_range(verse, bibleinfo):
    '''Returns a verse object with chapter and verse numbers corrected
    to lie within the ranges specified by bibleinfo.  If chapter and
    verse numbers are already in range then returns None.

    PVerse(None, ?, ?) => ValueError('Book must not be None!')
    PVerse(0, -1, X) => PVerse(0, 1, X)
    PVerse(0, 100000, X) => PVerse(0, 34, X)
    PVerse(0, 1, -1) => PVerse(0, 1, 1)
    '''

    range_error = False
    book = verse.book
    chapter = verse.chapter
    vnum = verse.verse

    num_chapters = len(bibleinfo[verse.book])
    if chapter is not None:
        if chapter < 1:
            range_error = True
            chapter = 1
        elif chapter > num_chapters:
            range_error = True
            chapter = num_chapters

    if vnum is not None:
        # Range of /chapter/ has been corrected, so it is guaranteed
        # valid by this point.  No check necessary.
        num_verses = bibleinfo[book][chapter - 1]
        if vnum < 1:
            range_error = True
            vnum = 1
        elif vnum > num_verses:
            range_error = True
            vnum = num_verses

    if range_error:
        return PVerse(book, chapter, vnum)
    else:
        return None


def _verse_partial_cmp(v1, v2):
    if v1.book < v2.book:
        return -1
    elif v1.book == v2.book:
        if v1.chapter is None or v2.chapter is None:
            return 0
        else:
            if v1.chapter < v2.chapter:
                return -1
            elif v1.chapter == v2.chapter:
                if v1.verse is None or v2.verse is None:
                    return 0
                else:
                    if v1.verse < v2.verse:
                        return -1
                    elif v1.verse == v2.verse:
                        return 0
                    else:
                        return 1
            else:
                return 1
    else:
        # assert v1.book > v2.book
        return 1


def _rectify_passage(passage, bibleinfo):
    '''
    @param passage: potentially malformed passage

    @type passage: PPassage
    '''

    passage_rectified = False

    new_spans = []
    for span in passage.spans:
        span_rectified = False

        first = _fix_verse_range(span.first, bibleinfo)
        last = _fix_verse_range(span.last, bibleinfo)

        if first is None:
            first = span.first
        else:
            span_rectified = True

        if last is None:
            last = span.last
        else:
            span_rectified = True

        if _verse_partial_cmp(first, last) > 0:
            # If first is after last, swap them to the correct order.
            span_rectified = True
            first, last = last, first

        # Fill in None values
        if first.book is None:
            raise ValueError('Book must not be None!')
        elif first.chapter is None:
            span_rectified = True
            first = PVerse(first.book, 1, 1)
        elif first.verse is None:
            span_rectified = True
            first = PVerse(first.book, first.chapter, 1)

        if last.book is None:
            raise ValueError('Book must not be None!')
        elif last.chapter is None:
            span_rectified = True
            last_chapter = len(bibleinfo[last.book])
            last_verse_of_chapter = bibleinfo[last.book][last_chapter - 1]
            last = PVerse(last.book, last_chapter, last_verse_of_chapter)
        elif last.verse is None:
            span_rectified = True
            last_verse_of_chapter = bibleinfo[last.book][last.chapter - 1]
            last = PVerse(last.book, last.chapter, last_verse_of_chapter)


        if span_rectified:
            new_span = PVerseSpan(first, last)
        else:
            passage_rectified = True
            new_span = span

        new_spans.append(new_span)

    new_spans.sort(_spancmp)
    new_spans = _fusespanlist(new_spans, bibleinfo)

    return PPassage(new_spans)


class PPassageRectifier(object):
    def __init__(self, token_iterable, bibleinfo):
        self._it = token_iterable
        self._bibleinfo = bibleinfo

    def __iter__(self):
        return self

    def next(self):
        t = self._it.next()

        if t.type == VFilterToken.PASSAGE:
            passage = t.value

            rectified_passage = _rectify_passage(passage, self._bibleinfo)
            return Token(t.type, rectified_passage, t.start, t.end, t.row, t.col)
        else:
            return t

