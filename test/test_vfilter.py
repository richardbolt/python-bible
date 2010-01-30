import unittest
import tokenizer
from tokenizer import Tokenizer
from tokenizer import WhitespaceFilter
from tokenizer import Token
from vfilter import _fusespans
from vfilter import _fusespanlist
from vfilter import PPassageRectifier
from vfilter import PPassageFilter
from vfilter import PVerseSpanFilter
from vfilter import PVerseFilter
from vfilter import BookFilter
from vfilter import BookMatcher
from vfilter import PPassage
from vfilter import PVerse
from vfilter import PVerseSpan
from vfilter import VFilterToken
from vfilter import _fix_verse_range
from vfilter import _rectify_passage
from vfilter import _verse_partial_cmp
from testbible import bibledef
from testbible import build_bibleinfo


class TestBookFilter(unittest.TestCase):
    def setUp(self):
        with open('books.txt') as f:
            self.matcher = BookMatcher.fromfile(f)


    def tokenStream(self, string):
        return tokenizer.WhitespaceFilter(Tokenizer(string))


    def test_filter_ofs(self):
        string = 'Genesis 4:12'
        tokens = list(BookFilter(self.tokenStream(string), self.matcher))
        self.assertEquals(len(tokens), 4)
        genesis, four, colon, twelve = tokens
        self.assertEquals(genesis.value, 0)
        self.assertEquals(genesis.start, 0)
        self.assertEquals(four.value, '4')
        self.assertEquals(colon.value, ':')
        self.assertEquals(twelve.value, '12')


class TestBookMatcher(unittest.TestCase):
    def setUp(self):
        with open('books.txt') as f:
            self.matcher = BookMatcher.fromfile(f)

    def tearDown(self):
        pass

    def test_books(self):
        matcher = self.matcher
        self.assertEquals(matcher.match('john'), 42)
        self.assertEquals(matcher.match('I Thessalonians'), 51)
        self.assertEquals(matcher.match('Genesis'), 0)
        self.assertEquals(matcher.match('adsfasd'), None)


class TestPVerseFilter(unittest.TestCase):
    def _tokenStream(self, string):
        with open('books.txt') as f:
            matcher = BookMatcher.fromfile(f)

        return PVerseFilter(BookFilter(WhitespaceFilter(Tokenizer(string)), matcher))

    def test_verse(self):
        tokenizer = self._tokenStream('John 3:16, flugelhorn genesis 5')
        self.assertTrue(tokenizer is not None)
        tokens = list(tokenizer)
        self.assertEquals(len(tokens), 4)
        john, comma, flugelhorn, genesis = tokens

        self.assertEquals(john, VFilterToken(VFilterToken.VERSE, PVerse(42, 3, 16), 0, 9, 1, 1))
        self.assertEquals(comma, Token(Token.SYMBOL, ',', 9, 10, 1, 10))
        self.assertEquals(flugelhorn, Token(Token.WORD, 'flugelhorn', 11, 21, 1, 12))
        self.assertEquals(genesis, VFilterToken(VFilterToken.VERSE, PVerse(0, 5, None), 22, 31, 1, 23))


class TestPVerseSpanFilter(unittest.TestCase):
    def _tokenStream(self, string):
        with open('books.txt') as f:
            matcher = BookMatcher.fromfile(f)

        return PVerseSpanFilter(BookFilter(WhitespaceFilter(Tokenizer(string)), matcher))

    def _xtest_verse(self):
        tokenizer = self._tokenStream('John 3:16, 17, 18, 19, 20 flugelhorn genesis 5')
        self.assertTrue(tokenizer is not None)
        tokens = list(tokenizer)
        for t in tokens:
            print t
        self.assertEquals(len(tokens), 4)
        john, comma, flugelhorn, genesis = tokens

        self.assertEquals(john, VFilterToken(VFilterToken.VERSE, PVerse(42, 3, 16), 0, 9, 1, 1))
        self.assertEquals(comma, Token(Token.SYMBOL, ',', 9, 10, 1, 10))
        self.assertEquals(flugelhorn, Token(Token.WORD, 'flugelhorn', 11, 21, 1, 12))
        self.assertEquals(genesis, VFilterToken(VFilterToken.VERSE, PVerse(0, 5, None), 22, 31, 1, 23))


class TestPPassageFilter(unittest.TestCase):
    def _tokenStream(self, string):
        with open('books.txt') as f:
            matcher = BookMatcher.fromfile(f)

        return PPassageFilter(BookFilter(tokenizer.WhitespaceFilter(Tokenizer(string)), matcher))


    def test_books(self):
        tokens = list(self._tokenStream('John - Acts'))
        self.assertEquals(len(tokens), 1)
        passage, = tokens
        self.assertEquals(len(passage.value), 1)

        tokens = list(self._tokenStream('John, Acts'))
        self.assertEquals(len(tokens), 1)
        passage, = tokens
        self.assertEquals(len(passage.value), 2)


    def test_chapter(self):
        tokens = list(self._tokenStream('John 3:16'))
        self.assertEquals(len(tokens), 1)
        passage, = tokens
        self.assertEquals(len(passage.value), 1)

        tokens = list(self._tokenStream('John 3:16,'))
        self.assertEquals(len(tokens), 2)
        passage, comma = tokens
        self.assertEquals(len(passage.value), 1)
        self.assertEquals(comma.value, ',')


    def test_verse(self):
        tokens = list(self._tokenStream('John 3:16'))
        self.assertEquals(len(tokens), 1)
        passage, = tokens
        self.assertEquals(len(passage.value), 1)

        tokens = list(self._tokenStream('John 3:16 - John 3:14'))
        self.assertEquals(len(tokens), 1)
        passage, = tokens
        self.assertEquals(len(passage.value), 1)


    def test_seeds(self):
        tokens = list(self._tokenStream('John 3-4'))
        self.assertEquals(len(tokens), 1)
        passage, = tokens
        self.assertEquals(len(passage.value), 1)
        self.assertEquals(passage.value.spans[0].first.chapter, 3)
        self.assertEquals(passage.value.spans[0].last.chapter, 4)

        tokens = list(self._tokenStream('John 3-4,5'))
        self.assertEquals(len(tokens), 1)
        passage, = tokens
        self.assertEquals(len(passage.value), 2)
        self.assertEquals(passage.value.spans[0].first.chapter, 3)
        self.assertEquals(passage.value.spans[0].last.chapter, 4)
        self.assertEquals(passage.value.spans[1].last.chapter, 5)

        tokens = list(self._tokenStream('Genesis,flugelhorn,Exodus,John 3-4,5, Acts 4:5-10'))
        self.assertEquals(len(tokens), 5)
        genesis, comma1, flugelhorn, comma2, long_passage = tokens
        self.assertEquals(len(long_passage.value), 4)
        self.assertEquals(long_passage.value.spans[3], PVerseSpan(PVerse(43, 4, 5), PVerse(43, 4, 10)))


    def test_chapter_and_verse_spanning_seed(self):
        tokens = list(self._tokenStream('Genesis 1:2 - 3:4'))
        self.assertEquals(len(tokens), 1)
        genesis, = tokens
        self.assertEquals(len(genesis.value.spans), 1)
        self.assertEquals(genesis.value.spans[0].first, PVerse(0, 1, 2))
        self.assertEquals(genesis.value.spans[0].last, PVerse(0, 3, 4))


    def test_book_spanning_seed(self):
        tokens = list(self._tokenStream('Genesis 1:2 - Exodus 2:3'))
        self.assertEquals(len(tokens), 1)
        passage, = tokens
        self.assertEquals(len(passage.value.spans), 1)
        self.assertEquals(passage.value.spans[0].first, PVerse(0, 1, 2))
        self.assertEquals(passage.value.spans[0].last, PVerse(1, 2, 3))


    def test_ne(self):
        self.assertFalse(PVerse(0, 1, 1,) != PVerse(0, 1, 1))
        self.assertTrue(PVerse(0, 1, 1,) != PVerse(0, 1, 2))


    def test_tokenization(self):
        string = 'John 3:x-16'
        tokens = list(self._tokenStream(string))
        self.assertEquals(len(tokens), 5)

        string = 'John 3,:x-16'
        tokens = list(self._tokenStream(string))
        self.assertEquals(len(tokens), 6)

        string = 'John 3,John 5 - John 6:x-16'
        tokens = list(self._tokenStream(string))
        self.assertEquals(len(tokens), 5)

        string = 'Nothing, ;John 3,John 5 - John 6:x-16'
        tokens = list(self._tokenStream(string))
        self.assertEquals(len(tokens), 8)

    def test_commas(self):
        tokenizer = self._tokenStream('John 3:16, 17, 18, 19, 20 flugelhorn\ngenesis 5')
        self.assertTrue(tokenizer is not None)
        tokens = list(tokenizer)
        self.assertEquals(len(tokens), 3)
        t_john, t_flugelhorn, t_genesis = tokens

        p = PPassage((
                PVerseSpan(PVerse(42, 3, 16), PVerse(42, 3, 16)),
                PVerseSpan(PVerse(42, 3, 17), PVerse(42, 3, 17)),
                PVerseSpan(PVerse(42, 3, 18), PVerse(42, 3, 18)),
                PVerseSpan(PVerse(42, 3, 19), PVerse(42, 3, 19)),
                PVerseSpan(PVerse(42, 3, 20), PVerse(42, 3, 20)),
            ))
        self.assertEquals(t_john, VFilterToken(VFilterToken.PASSAGE, p, 0, 25, 1, 1))
        self.assertEquals(t_flugelhorn, Token(Token.WORD, 'flugelhorn', 26, 36, 1, 27))

        p = PPassage((
                PVerseSpan(PVerse(0, 5, None), PVerse(0, 5, None)),
            ))
        self.assertEquals(t_genesis, VFilterToken(VFilterToken.PASSAGE, p, 37, 46, 2, 1))




class TestSpanFusing(unittest.TestCase):
    def __init__(self, *args, **keywords):
        super(type(self), self).__init__(*args, **keywords)

        self.bibleinfo = build_bibleinfo()

    def test_fusespans_a(self):
        s1 = PVerseSpan(PVerse(0, 1, 1), PVerse(0, 1, 10))
        s2 = PVerseSpan(PVerse(0, 1, 12), PVerse(0, 1, 13))
        self.assertRaises(ValueError, _fusespans, s1, s2, self.bibleinfo)

        s1 = PVerseSpan(PVerse(0, 1, 1), PVerse(0, 1, 10))
        s2 = PVerseSpan(PVerse(0, 1, 11), PVerse(0, 1, 12))
        expected = PVerseSpan(PVerse(0, 1, 1), PVerse(0, 1, 12))
        self.assertEquals(_fusespans(s1, s2, self.bibleinfo), expected)

        s1 = PVerseSpan(PVerse(0, 1, 1), PVerse(0, 1, 10))
        s2 = PVerseSpan(PVerse(0, 1, 10), PVerse(0, 1, 11))
        expected = PVerseSpan(PVerse(0, 1, 1), PVerse(0, 1, 11))
        self.assertEquals(_fusespans(s1, s2, self.bibleinfo), expected)

        s1 = PVerseSpan(PVerse(0, 1, 1), PVerse(0, 1, 10))
        s2 = PVerseSpan(PVerse(0, 1, 5), PVerse(0, 1, 10))
        expected = PVerseSpan(PVerse(0, 1, 1), PVerse(0, 1, 10))
        self.assertEquals(_fusespans(s1, s2, self.bibleinfo), expected)

        s1 = PVerseSpan(PVerse(0, 1, 1), PVerse(0, 1, 10))
        s2 = PVerseSpan(PVerse(0, 1, 5), PVerse(0, 1, 9))
        expected = PVerseSpan(PVerse(0, 1, 1), PVerse(0, 1, 10))
        self.assertEquals(_fusespans(s1, s2, self.bibleinfo), expected)

        s1 = PVerseSpan(PVerse(0, 1, 10), PVerse(0, 1, 20))
        s2 = PVerseSpan(PVerse(0, 1, 10), PVerse(0, 1, 11))
        expected = PVerseSpan(PVerse(0, 1, 10), PVerse(0, 1, 20))
        self.assertEquals(_fusespans(s1, s2, self.bibleinfo), expected)

        s1 = PVerseSpan(PVerse(0, 1, 10), PVerse(0, 1, 20))
        s2 = PVerseSpan(PVerse(0, 1, 9), PVerse(0, 1, 10))
        expected = PVerseSpan(PVerse(0, 1, 9), PVerse(0, 1, 20))
        self.assertEquals(_fusespans(s1, s2, self.bibleinfo), expected)

        s1 = PVerseSpan(PVerse(0, 1, 10), PVerse(0, 1, 20))
        s2 = PVerseSpan(PVerse(0, 1, 8), PVerse(0, 1, 9))
        expected = PVerseSpan(PVerse(0, 1, 8), PVerse(0, 1, 20))
        self.assertEquals(_fusespans(s1, s2, self.bibleinfo), expected)

        s1 = PVerseSpan(PVerse(0, 1, 10), PVerse(0, 1, 20))
        s2 = PVerseSpan(PVerse(0, 1, 8), PVerse(0, 1, 8))
        self.assertRaises(ValueError, _fusespans, s1, s2, self.bibleinfo)


    def test_fusespans_b(self):
        s1 = PVerseSpan(PVerse(0, 1, 22), PVerse(0, 1, 23))
        s2 = PVerseSpan(PVerse(0, 1, 10), PVerse(0, 1, 20))
        self.assertRaises(ValueError, _fusespans, s1, s2, self.bibleinfo)

        s1 = PVerseSpan(PVerse(0, 1, 21), PVerse(0, 1, 22))
        s2 = PVerseSpan(PVerse(0, 1, 10), PVerse(0, 1, 20))
        expected = PVerseSpan(PVerse(0, 1, 10), PVerse(0, 1, 22))
        self.assertEquals(_fusespans(s1, s2, self.bibleinfo), expected)

        s1 = PVerseSpan(PVerse(0, 1, 20), PVerse(0, 1, 21))
        s2 = PVerseSpan(PVerse(0, 1, 10), PVerse(0, 1, 20))
        expected = PVerseSpan(PVerse(0, 1, 10), PVerse(0, 1, 21))
        self.assertEquals(_fusespans(s1, s2, self.bibleinfo), expected)

        s1 = PVerseSpan(PVerse(0, 1, 15), PVerse(0, 1, 16))
        s2 = PVerseSpan(PVerse(0, 1, 10), PVerse(0, 1, 20))
        expected = PVerseSpan(PVerse(0, 1, 10), PVerse(0, 1, 20))
        self.assertEquals(_fusespans(s1, s2, self.bibleinfo), expected)

        s1 = PVerseSpan(PVerse(0, 1, 10), PVerse(0, 1, 12))
        s2 = PVerseSpan(PVerse(0, 1, 10), PVerse(0, 1, 20))
        expected = PVerseSpan(PVerse(0, 1, 10), PVerse(0, 1, 20))
        self.assertEquals(_fusespans(s1, s2, self.bibleinfo), expected)

        s1 = PVerseSpan(PVerse(0, 1, 9), PVerse(0, 1, 11))
        s2 = PVerseSpan(PVerse(0, 1, 10), PVerse(0, 1, 20))
        expected = PVerseSpan(PVerse(0, 1, 9), PVerse(0, 1, 20))
        self.assertEquals(_fusespans(s1, s2, self.bibleinfo), expected)

        s1 = PVerseSpan(PVerse(0, 1, 9), PVerse(0, 1, 10))
        s2 = PVerseSpan(PVerse(0, 1, 10), PVerse(0, 1, 20))
        expected = PVerseSpan(PVerse(0, 1, 9), PVerse(0, 1, 20))
        self.assertEquals(_fusespans(s1, s2, self.bibleinfo), expected)

        s1 = PVerseSpan(PVerse(0, 1, 8), PVerse(0, 1, 9))
        s2 = PVerseSpan(PVerse(0, 1, 10), PVerse(0, 1, 20))
        expected = PVerseSpan(PVerse(0, 1, 8), PVerse(0, 1, 20))
        self.assertEquals(_fusespans(s1, s2, self.bibleinfo), expected)

        s1 = PVerseSpan(PVerse(0, 1, 10), PVerse(0, 1, 20))
        s2 = PVerseSpan(PVerse(0, 1, 10), PVerse(0, 1, 20))
        expected = PVerseSpan(PVerse(0, 1, 10), PVerse(0, 1, 20))
        self.assertEquals(_fusespans(s1, s2, self.bibleinfo), expected)

        s1 = PVerseSpan(PVerse(0, 1, 8), PVerse(0, 1, 8))
        s2 = PVerseSpan(PVerse(0, 1, 10), PVerse(0, 1, 20))
        self.assertRaises(ValueError, _fusespans, s1, s2, self.bibleinfo)


    def test_fusespanlist(self):
        spans = [
            PVerseSpan(PVerse(0, 1, 1), PVerse(0, 1, 10)),
            PVerseSpan(PVerse(0, 1, 2), PVerse(0, 1, 3)),
        ]
        expected = [
            PVerseSpan(PVerse(0, 1, 1), PVerse(0, 1, 10)),
        ]
        self.assertEquals(_fusespanlist(spans, self.bibleinfo), expected)

        spans = [
            PVerseSpan(PVerse(0, 1, 1), PVerse(0, 1, 6)),
            PVerseSpan(PVerse(0, 1, 1), PVerse(0, 1, 10)),
        ]
        expected = [
            PVerseSpan(PVerse(0, 1, 1), PVerse(0, 1, 10)),
        ]
        self.assertEquals(_fusespanlist(spans, self.bibleinfo), expected)


class TestPPassageRectifier(unittest.TestCase):
    def __init__(self, *args, **keywords):
        super(type(self), self).__init__(*args, **keywords)

        self.bibleinfo = build_bibleinfo()


    def _tokenStream(self, string):
        with open('books.txt') as f:
            matcher = BookMatcher.fromfile(f)

        return PPassageFilter(BookFilter(tokenizer.WhitespaceFilter(Tokenizer(string)), matcher))

    def _rectifiedStream(self, string):
        return PPassageRectifier(self._tokenStream(string), self.bibleinfo)


    def test_reordering(self):
        tokens = list(self._rectifiedStream('Exodus, Genesis'))
        self.assertEquals(len(tokens), 1)
        passage = tokens[0].value
        self.assertEquals(len(passage), 2)
        self.assertEquals(passage.spans[0], PVerseSpan(PVerse(0, 1, 1), PVerse(0, 34, 19)))
        self.assertEquals(passage.spans[1], PVerseSpan(PVerse(1, 1, 1), PVerse(1, 35, 1)))


    def test_fusing(self):
        tokens = list(self._rectifiedStream('Genesis 1, Genesis'))
        self.assertEquals(len(tokens), 1)
        passage = tokens[0].value
        self.assertEquals(len(passage), 1)
        self.assertEquals(passage.spans[0], PVerseSpan(PVerse(0, 1, 1), PVerse(0, 34, 19)))

        tokens = list(self._rectifiedStream('Genesis 1:10-20, Genesis 1:21'))
        self.assertEquals(len(tokens), 1)
        passage = tokens[0].value
        self.assertEquals(len(passage), 1)
        self.assertEquals(passage.spans[0], PVerseSpan(PVerse(0, 1, 10), PVerse(0, 1, 21)))

    def test_book(self):
        string = 'Genesis'
        tokens = list(self._rectifiedStream(string))
        self.assertEquals(len(tokens), 1)
        passage = tokens[0].value
        self.assertEquals(len(passage.spans), 1)
        self.assertEquals(passage.spans[0], PVerseSpan(PVerse(0, 1, 1), PVerse(0, 34, 19)))

    def test_chapter(self):
        string = 'John 3'
        tokens = list(self._rectifiedStream(string))
        self.assertEquals(len(tokens), 1)
        passage = tokens[0].value
        self.assertEquals(len(passage.spans), 1)
        self.assertEquals(passage.spans[0], PVerseSpan(PVerse(42, 3, 1), PVerse(42, 3, 36)))

    def test_verse(self):
        string = 'John 3 - John 3:16'

        tokens = list(self._rectifiedStream(string))
        self.assertEquals(len(tokens), 1)
        passage = tokens[0].value
        self.assertEquals(len(passage.spans), 1)
        self.assertEquals(passage.spans[0], PVerseSpan(PVerse(42, 3, 1), PVerse(42, 3, 16)))


class TestRectifyPassageFunc(unittest.TestCase):
    def __init__(self, *args, **keywords):
        super(type(self), self).__init__(*args, **keywords)

        self._bibleinfo = build_bibleinfo()


    def assertRectifies(self, miscreant, expected):
        self.assertEquals(_rectify_passage(PPassage(miscreant), self._bibleinfo), PPassage(expected))


    def test_fix_range(self):
        '''Correct verse chapter and verse ranges: Genesis 0 - 99999 => Genesis 1 - 34'''

        # In range
        self.assertEquals(_fix_verse_range(PVerse(0, 1, 1), self._bibleinfo), None)

        # Chapter out of range
        self.assertEquals(_fix_verse_range(PVerse(0, 0, None), self._bibleinfo), PVerse(0, 1, None))
        self.assertEquals(_fix_verse_range(PVerse(0, 99999, None), self._bibleinfo), PVerse(0, 34, None))

        # Verse out of range
        self.assertEquals(_fix_verse_range(PVerse(0, 1, 0), self._bibleinfo), PVerse(0, 1, 1))
        self.assertEquals(_fix_verse_range(PVerse(0, 1, 999999), self._bibleinfo), PVerse(0, 1, 31))

        # Chapter and verse out of range
        self.assertEquals(_fix_verse_range(PVerse(0, 0, 0), self._bibleinfo), PVerse(0, 1, 1))
        self.assertEquals(_fix_verse_range(PVerse(0, 999, 999), self._bibleinfo), PVerse(0, 34, 19))


    def test_endpoint_swap(self):
        '''Swap span endpoints: Genesis 1:20 - 5 => Genesis 1:5-20'''
        miscreant = [
            PVerseSpan(PVerse(0, 34, None), PVerse(0, 1, None)),
        ]
        expected = [
            PVerseSpan(PVerse(0, 1, 1), PVerse(0, 34, 19)),
        ]

        self.assertRectifies(miscreant, expected)


class TestPartialVerseCmp(unittest.TestCase):
    def test_cmp(self):
        self.assertEquals(_verse_partial_cmp(PVerse(42, 3, None), PVerse(42, 3, 16)), 0)
        self.assertEquals(_verse_partial_cmp(PVerse(42, 2, None), PVerse(42, 3, 16)), -1)
        self.assertEquals(_verse_partial_cmp(PVerse(42, 4, None), PVerse(42, 3, 16)), 1)
        self.assertEquals(_verse_partial_cmp(PVerse(42, 3, None), PVerse(42, 3, None)), 0)
        self.assertEquals(_verse_partial_cmp(PVerse(42, 2, None), PVerse(42, 3, None)), -1)


if __name__ == '__main__':
    unittest.main()
