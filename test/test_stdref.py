import unittest
from vfilter import BookMatcher

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

        print formatter.format(t.value)

    def test_search(self):
        string = "Glory, I'm back home Genesis 16:32 - Genesis 3\n in Exodus 1:10 - Exodus 1:5 Canada"
        tokens = list(search(string, MATCHER, BIBLEINFO))

        for t in tokens:
            print t.row, t.col, string[t.start:t.end], '=>', formatter.format(t.value)


if __name__ == '__main__':
    unittest.main()
