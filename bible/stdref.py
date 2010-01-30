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
            return self._format_passage(passage_span_or_verse)
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
            raise ValueError('Is not a token!')

    return passage_token


def search(string, matcher, bibleinfo):
    it = tokenizer(string, matcher, bibleinfo)

    for t in it:
        if t.type == VFilterToken.PASSAGE:
            yield t
    else:
        raise StopIteration()
