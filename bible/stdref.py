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
