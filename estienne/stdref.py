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

'''Standard bible model and references.'''

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


 #~ |  add(...)
 #~ |      Add an element to a set.
 #~ |
 #~ |      This has no effect if the element is already present.
 #~ |
 #~ |  clear(...)
 #~ |      Remove all elements from this set.
 #~ |
 #~ |  copy(...)
 #~ |      Return a shallow copy of a set.
 #~ |
 #~ |  difference(...)
 #~ |      Return the difference of two or more sets as a new set.
 #~ |
 #~ |      (i.e. all elements that are in this set but not the others.)
 #~ |
 #~ |  difference_update(...)
 #~ |      Remove all elements of another set from this set.
 #~ |
 #~ |  discard(...)
 #~ |      Remove an element from a set if it is a member.
 #~ |
 #~ |      If the element is not a member, do nothing.
 #~ |
 #~ |  intersection(...)
 #~ |      Return the intersection of two sets as a new set.
 #~ |
 #~ |      (i.e. all elements that are in both sets.)
 #~ |
 #~ |  intersection_update(...)
 #~ |      Update a set with the intersection of itself and another.
 #~ |
 #~ |  isdisjoint(...)
 #~ |      Return True if two sets have a null intersection.
 #~ |
 #~ |  issubset(...)
 #~ |      Report whether another set contains this set.
 #~ |
 #~ |  issuperset(...)
 #~ |      Report whether this set contains another set.
 #~ |
 #~ |  pop(...)
 #~ |      Remove and return an arbitrary set element.
 #~ |      Raises KeyError if the set is empty.
 #~ |
 #~ |  remove(...)
 #~ |      Remove an element from a set; it must be a member.
 #~ |
 #~ |      If the element is not a member, raise a KeyError.
 #~ |
 #~ |  symmetric_difference(...)
 #~ |      Return the symmetric difference of two sets as a new set.
 #~ |
 #~ |      (i.e. all elements that are in exactly one of the sets.)
 #~ |
 #~ |  symmetric_difference_update(...)
 #~ |      Update a set with the symmetric difference of itself and another.
 #~ |
 #~ |  union(...)
 #~ |      Return the union of sets as a new set.
 #~ |
 #~ |      (i.e. all elements that are in either set.)
 #~ |
 #~ |  update(...)
 #~ |      Update a set with the union of itself and others.
class VerseSetBehaviour(object):
    def isdisjoint(self, other):
        '''Return True if two sets have a null intersection.'''
        pass

    def issubset(self, other):
        '''Report whether another set contains this set.'''
        pass

    def issuperset(self, other):
        '''Report whether this set contains another set.'''
        pass



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


class SpanSet(BibleRef):
    def __init__(self, model, arg):
        BibleRef.__init__(self, model)
        self._spans = tuple(VerseSpan(s.first, s.last, model) for s in spans)

    @property
    def spans(self):
        return self._spans


    def __iter__(self):
        return iter(self._spans)


class Passage(BibleRef):
    '''Creates a passage to represent `arg` where `arg` is an
    iterable of unsorted/overlapping :class:`VerseSpan` objects and
    :class:`model` is a :class:`BibleModel` object.

    Passages are ordered lists of non-contiguous, non-overlapping
    unique verses.
    '''

    def __init__(self, model, arg):
        BibleRef.__init__(self, model)

        if type(arg) is str:
            t = self.model.match(arg)
            fused_spans = tuple(model.Span(model.Verse(s.first.book, s.first.chapter, s.first.verse), model.Verse(s.last.book, s.last.chapter, s.last.verse)) for s in t.value.spans)
        else:
            spans = arg
            fused_spans = tuple(model.Span(model.Verse(s.first.book, s.first.chapter, s.first.verse), model.Verse(s.last.book, s.last.chapter, s.last.verse)) for s in _fusespanlist(spans, model.bibleinfo))
        #~ else:
            #~ raise TypeError('unsupported type %s' % repr(reference_or_spans))

        self._spans = fused_spans


    @property
    def spans(self):
        return self._spans


    def __len__(self):
        '''Returns the number of :class:`VerseSpan` objects in the passage.'''
        return len(self._spans)


    def __iter__(self):
        return iter(self._spans)


    def issuperset(self, other):
        '''True if this passage contains all verses in `other` and False
        otherwise; `other` is  a  is a :class:`Verse`,
        :class:`VerseSpan`, or :class:`Passage` object.'''

        # Very niave implementation, but it works.
        rc = False
        if is_verse(other) or is_span(other):
            for s in self.spans:
                if s.issuperset(other):
                    rc = True
        elif is_passage(other):
            rc = True
            for other_span in other.spans:
                for self_span in self.spans:
                    if self_span.issuperset(other_span):
                        break
                else:
                    rc = False
                    break
        else:
            raise TypeError()

        return rc



def _count_span_verses(span):
    '''Counts the number of verses in a VerseSPan.'''

    num_verses = 0
    for book_idx in xrange(span.first.book, span.last.book + 1):
        start_chapter_idx = 0
        stop_chapter_idx = len(span.model.bibleinfo[book_idx])

        if book_idx == span.first.book:
            start_chapter_idx = span.first.chapter - 1

        if book_idx == span.last.book:
            stop_chapter_idx = span.last.chapter

        for chapter_idx in xrange(start_chapter_idx, stop_chapter_idx):
            start_verse_idx = 0
            stop_verse_idx = span.model.bibleinfo[book_idx][chapter_idx]

            if book_idx == span.first.book and chapter_idx == span.first.chapter - 1:
                start_verse_idx = span.first.verse - 1

            if book_idx == span.last.book and chapter_idx == span.last.chapter - 1:
                stop_verse_idx = span.last.verse

            num_verses += stop_verse_idx - start_verse_idx

    return num_verses


class VerseSpan(BibleRef):
    '''An ordered list of contiguous, unique verses.'''
    def __init__(self, first, last, model):
        BibleRef.__init__(self, model)
        self._first = first
        self._last = last
        self.__len = _count_span_verses(self)

    @property
    def first(self):
        return self._first

    @property
    def last(self):
        return self._last


    def isdisjoint(self, other):
        '''Return True if two sets have a null intersection.'''
        raise NotImplementedError()


    def issubset(self, other):
        '''Report whether another set contains this set.'''
        raise NotImplementedError()


    def issuperset(self, other):
        '''True if this span contains all verses in `other` and False
        otherwise; `other` is  a  is a :class:`Verse`,
        :class:`VerseSpan`, or :class:`Passage` object.'''

        rc = False
        if is_verse(other):
            if self.first <= other and other <= self.last:
                rc = True
        elif is_span(other):
            if self.first <= other.first and other.last <= self.last:
                rc = True
        elif is_passage(other):
            rc = True
            for span in other:
                rc = rc and self.issuperset(span)
        else:
            raise TypeError()

        return rc


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
        '''Verse book id: `int`.'''
        return self._book

    @property
    def chapter(self):
        '''Verse chapter: `int`.'''
        return self._chapter

    @property
    def verse(self):
        '''Verse number: `int`.'''
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
            # Exodus
            return self._lut[first.book]
        elif span.first == span.last:
            # Genesis 5:1
            return self._format_verse(span.first)
        elif first.chapter == 1 and first.verse == 1 and \
                    last.chapter == len(span.model.bibleinfo[last.book]) and last.verse == span.model.bibleinfo[last.book][last.chapter - 1]:
            # Exodus - Leviticus
            return '%s - %s' % (self._lut[first.book], self._lut[last.book])
        elif first.book == last.book and first.chapter == last.chapter and \
                first.verse == 1 and \
                last.verse == span.model.bibleinfo[last.book][last.chapter - 1]:
            # Genesis 5
            return '%s %d' % (self._lut[first.book], first.chapter)
        elif first.book == last.book and first.chapter == last.chapter:
            # Genesis 1:5-10
            return '%s %d:%d - %d' % (self._lut[first.book], first.chapter, first.verse, last.verse)
        elif first.book == last.book:
            # Genesis 4:5 - 6:4
            return '%s %d:%d - %d:%d' % (self._lut[first.book], first.chapter, first.verse, last.chapter, last.verse)
        else:
            # Genesis 4:5 - Exodus 5:12
            return '%s %d:%d - %s %d:%d' % (self._lut[first.book], first.chapter, first.verse, self._lut[last.book], last.chapter, last.verse)

    def _format_verse(self, verse):
        return '%s %d:%d' % (self._lut[verse.book], verse.chapter, verse.verse)


    def booktitle(self, book_idx):
        return self._lut[book_idx]


    def format(self, passage_span_or_verse):
        if hasattr(passage_span_or_verse, 'spans'):
            return self._format_passage(passage_span_or_verse)
        elif hasattr(passage_span_or_verse, 'first') and hasattr(passage_span_or_verse, 'last'):
            return self._format_span(passage_span_or_verse)
        elif hasattr(passage_span_or_verse, 'book') and hasattr(passage_span_or_verse, 'chapter') and hasattr(passage_span_or_verse, 'verse'):
            return self._format_verse(passage_span_or_verse)
        else:
            raise Exception('Unknown type')


def tokenizer(string, bookmatcher, bibleinfo):
    tokenizer = Tokenizer(string)
    f0 = WhitespaceFilter(tokenizer)
    f1 = BookFilter(f0, bookmatcher)
    f2 = PPassageFilter(f1)
    f3 = PPassageRectifier(f2, bibleinfo)

    return f3


def match(string, bookmatcher, bibleinfo):
    '''Match a verse reference.

    :param string: string to match.
    :param bookmatcher:
    :type bookmatcher: .. class::`estienne.vfilter.BookMatcher`'''
    it = tokenizer(string, bookmatcher, bibleinfo)

    passage_token = None
    for t in it:
        if t.type == VFilterToken.PASSAGE:
            passage_token = t
        else:
            break

    if passage_token is None:
        raise ValueError('string %s is not a valid passage' % repr(string))

    return passage_token


def search(string, bookmatcher, bibleinfo):
    it = tokenizer(string, bookmatcher, bibleinfo)

    for t in it:
        if t.type == VFilterToken.PASSAGE:
            yield t
    else:
        raise StopIteration()


class BibleModel(object):
    def __init__(self, bibleinfo, bookmatcher, formatter):
        self._bibleinfo = bibleinfo
        self._bookmatcher = bookmatcher
        self._formatter = formatter
        self._offsets = self.build_offsets()


    def build_offsets(self):
        offsets = []

        ofs = 0
        for book_idx in xrange(0, len(self.bibleinfo)):
            chapter_offsets = []
            for chapter_idx in xrange(0, len(self.bibleinfo[book_idx])):
                chapter_offsets.append(ofs)
                ofs += self.bibleinfo[book_idx][chapter_idx]

            offsets.append(tuple(chapter_offsets))

        return tuple(offsets)


    def Passage(self, arg):
        return Passage(self, arg)


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
            Chapter(book: int, chapter: int)
            Chapter(book: str, chapter: int) # not presently supported
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
            book_idx = self._bookmatcher.match(args[0])
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
        passage = match(string, self._bookmatcher, self._bibleinfo)
        return passage


    def matchbook(self, string):
        return self._bookmatcher.match(string)


    def search(self, string):
        for p in search(string, self._bookmatcher, self._bibleinfo):
            yield p

    def tokens(self, string):
        for t in tokenizer(string, self._bookmatcher, self._bibleinfo):
            yield t

    def format(self, string):
        return self.formatter.format(string)


    @property
    def bibleinfo(self):
        return self._bibleinfo


    @property
    def offsets(self):
        return self._offsets


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
        elif self._last < self._span.last:
            bibleinfo = self._last.model.bibleinfo

            book_idx = self._last.book
            chapter_idx = self._last.chapter - 1
            verse = self._last.verse

            if verse < bibleinfo[book_idx][chapter_idx]:
                n = self._span.model.Verse(book_idx, chapter_idx + 1, verse + 1)
            elif chapter_idx + 1 < len(bibleinfo[book_idx]):
                n = self._span.model.Verse(book_idx, chapter_idx + 2, 1)
            elif book_idx < len(bibleinfo) - 1:
                n = self._span.model.Verse(book_idx + 1, 1, 1)
            else:
                raise StopIteration()

            self._last = n
        else:
            raise StopIteration()

        return self._last


def verse_iter(arg):
    if is_passage(arg):
        p = arg # passage
        it = chain(*[iter(s) for s in p])
    elif is_span(arg):
        span = arg # span
        it = iter(span)
    elif is_verse(arg):
        v = arg # verse
        it = iter((v,))
    else:
        raise TypeError('Unknown type %s' % type(arg))

    return it


def is_passage(o):
    if hasattr(o, 'spans'):
        return True
    else:
        return False


def is_span(o):
    if hasattr(o, 'first') and hasattr(o, 'last'):
        return True
    else:
        return False


def is_verse(o):
    if hasattr(o, 'book') and hasattr(o, 'chapter') and hasattr(o, 'verse'):
        return True
    else:
        return False


def count_verses(*args):
    num_verses = 0

    if len(args) == 1:
        arg = args[0]
        if is_passage(arg):
            passage = arg
            for s in passage.spans:
                num_verses += _count_span_verses(s)
        elif is_span(arg):
            num_verses = _count_span_verses(arg)
        elif is_verse(arg):
            num_verses = 1
        else:
            raise TypeError('unrecognized type; cannot extract verses.')
    else:
        raise TypeError('incorrect number of arguments to count_verses()')

    return num_verses




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
