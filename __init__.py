import re
import string
import data

# regular expressions for matching a valid normalized verse string
verse_re = re.compile(r'^\d{1,2}-\d{1,3}-\d{1,3}$')

# regular expressions for identifying book, and chapter:verse references
book_re = re.compile(r'^\d*[a-zA-Z ]*')
ref_re = re.compile(r'\d{1,3}:\d{1,3}')

# get bible data from data.py
bible = data.bible_data()

class Verse:
    """Class to represent a Bible reference (book, chapter, and verse)"""
    
    def __init__(self, *args):
        """Create a new Verse object - accepts several different inputs:
        
        Examples: book = 45
                  chapter = 2
                  verse = 1
                  Verse(book, chapter, verse)

                  normalized_string = '45-2-1'
                  Verse(normalized_string)

                  unformatted_string = '1 Cor 2:1'
                  Verse(unformatted_string)"""
        
        
        # if we got 3 values, let's assume they are book, chapter, verse)
        if len(args) == 3:
            values = args
            
        # if we only got one value, lets try to figure it out
        elif len(args) == 1:
            
            # maybe we got a normalized b-c-v string
            try:
                values = self._get_values(args[0])
            
            # if not, let's try to normalize it first and then extract values
            except:
                normalized = self._normalize(args[0])
                values = self._get_values(normalized)
        self.book = int(values[0])
        self.chapter = int(values[1])
        self.verse = int(values[2])
    
    def __unicode__(self):
        return self.format('B C:V')
    
    def format(self, val):
        """Return a formatted string to represent the verse
        Letters are substituted for verse attributes, like date formatting
        
        A - Book abbreviation (e.g. "Gen", "Rom")
        B - Full book name (e.g. "Genesis", "Romans")
        C - Chapter number
        V - Verse number"""
        
        val = string.replace(val,'B', bible[self.book]['name'])
        val = string.replace(val,'A', bible[self.book]['abbrs'][0].title())
        val = string.replace(val,'C', str(self.chapter))
        val = string.replace(val,'V', str(self.verse))
        return val

    def to_string(self):
        """Casts a verse object into a normalized string
        This is especially useful for saving to a database"""
        
        return str(self.book) + '-' + str(self.chapter) + '-' + str(self.verse)

    def _normalize(self, value):
        """Try to figure out what verse is intended when given an unstructured string
        and return the standard b-c-v formatted string for the verse.
        
        E.g. "1cor12:1", "1 Cor 12:1", and "1c 12:1" would all evaluate to "45-12-1" """

        # dict to hold processed data
        processed = {}

        # find the book reference
        try:
            b = book_re.search(value).group(0)
        except:
            raise Exception("We can't find that book of the Bible: %s" % (value))

        # find the chapter:verse reference
        try:
            ref = ref_re.search(value).group(0)
        except:
            raise Exception("We can't make sense of your chapter:verse reference")

        # try to find the book listed as a book name or abbreviation
        b = b.rstrip('.').lower().strip()
        for i, book in enumerate(bible):
            if book['name'].lower() == b:
                processed['book'] = i
                break
            else:
                for abbr in book['abbrs']:
                    if abbr == b:
                        processed['book'] = i
                        break
        if 'book' not in processed:
            raise Exception("We can't find that book of the Bible!: %s" % (b))

        # extract chapter and verse from ref
        c, v = map(int, ref.split(':'))

        # check to see if the chapter is in range for the given book
        try:
            verse_count = bible[processed['book']]['verse_counts'][c-1]
            processed['chapter'] = c
        except:
            raise Exception("There are not that many chapters in %s" % (bible[processed['book']]['name']))

        # check to see if the verse is in range for the given chapter
        if verse_count < v:
            raise Exception("There is no verse %s in %s %s" % (v, bible[processed['book']]['name'], c))
        else:
            processed['verse'] = v

        # return the processed data as a normalized verse string in b-c-v format
        return str(processed['book']) + '-' + str(processed['chapter']) + '-' + str(processed['verse'])

    def _get_values(self, value):
        """Expects a normalized string in b-c-v format - Given a b-c-v string,
        returns a tuple of the individual values
        
        E.g. "45-12-1" returns (45,12,1), after checking to make sure the verse exists"""
    
        if value is None:
            return False

        if not verse_re.search(value):
            raise Exception('String should be in normalized b-c-v format.')
    
        # now that we have the date string in B-C-V format, check to make
        # sure it's a valid verse.
        book, chapter, verse = map(int, value.split('-'))
    
        try:
            if bible[book]['verse_counts'][chapter-1] >= verse:
                return (book, chapter, verse)
        except:
            raise Exception('The verse specified does not exist.')


class Passage:
    """A passage of scripture with start and end verses"""
    
    def __init__(self, start, end):
        """Create a new Passage object - accepts Verse objects or any
        string inputs that can process into valid Verse objects
        
        Examples: v1 = Verse('Rom. 1:1')
                  v2 = Verse('Rom. 1:8')
                  Passage(v1, v2)
                  
                  Passage('Rom. 1:1', 'Rom. 1:8')"""
                  
        if start.__class__ == Verse:
            self.start = start
        else:
            self.start = Verse(start)
        if end.__class__ == Verse:
            self.end = end
        else:
            self.end = Verse(end)
    
    def __unicode__(self):
        return self.smart_format()
    
    def length(self):
        """count the total number of verses in the passage"""
        
        # start and end are in the same book
        if self.start.book == self.end.book:
            
            # start and end are in the same chapter of the same book
            if self.start.chapter == self.end.chapter:
                count = self.end.verse - self.start.verse + 1
            
            # start and end are in different chapters of the same book
            else:
                
                # get number of verses in start chapter
                count = bible[self.start.book]['verse_counts'][self.start.chapter - 1] - self.start.verse + 1

                # add number of verses in whole chapters between start and end
                for chapter in range(self.start.chapter + 1, self.end.chapter):
                    count += bible[self.start.book]['verse_counts'][chapter - 1]
                
                # add the number of verses in the end chapter
                count += self.end.verse
        
        # start and end are in different books
        else:

            # get number of verses in first chapter of start book
            count = bible[self.start.book]['verse_counts'][self.start.chapter - 1] - self.start.verse + 1
            
            # add number of verses in whole chapters of start book
            for chapter in range(self.start.chapter, len(bible[self.start.book]['verse_counts'])):
                count += bible[self.start.book]['verse_counts'][chapter]
            
            # add total number of verses in whole books between start and end
            for book in range(self.start.book + 1, self.end.book):
                for chapter_count in bible[book]['verse_counts']:
                    count += chapter_count
            
            # add number of verses in whole chapters of end book
            for chapter in range(1, self.end.chapter):
                count += bible[self.end.book]['verse_counts'][chapter - 1]
            
            # get the number of verses in last chapter of end book
            count += self.end.verse
        
        # return the count
        return count
    
    def format(self, val):
        """Return a formatted string to represent the passage
        Letters are substituted for verse attributes, like date formatting
        
        A - Book abbreviation (e.g. "Gen", "Rom")
        B - Full book name (e.g. "Genesis", "Romans")
        C - Chapter number
        V - Verse number
        
        Lowercase letters (a, b, c, and v) refer to end verse reference"""
        
        # create blank string to hold output
        f = ""
        
        # iterate over letters in val string passed in to method
        for c in val:
            
            # replace vals for start verse
            if c == "B":
                f += bible[self.start.book]['name']
            elif c == "A":
                f += bible[self.start.book]['abbrs'][0].title()
            elif c == "C":
                f += str(self.start.chapter)
            elif c == "V":
                f += str(self.start.verse)
            
            # replace vals for end verse
            elif c == "b":
                f += bible[self.end.book]['name']
            elif c == "a":
                f += bible[self.end.book]['abbrs'][0].title()
            elif c == "c":
                f += str(self.end.chapter)
            elif c == "v":
                f += str(self.end.verse)
            
            # if this isn't a format char, just pass it through to output
            else:
                f += c
        
        # return formatted string
        return f
    
    def smart_format(self):
        """Display a human-readible string for passage
        E.g. Start:  Rom. 12:1
             End:    Rom. 12:8
             Output: Romans 12:1-8
             ------
             Start:  Rom. 1:1
             End:    Rom. 2:1
             Output: Romans 1:1 - 2:1
             ------
             Start:  Acts 1:1
             End:    Rom. 1:1
             Output: Acts 1:1 - Romans 1:1"""
        
        # start and end are in the same book
        if self.start.book == self.end.book:
            
            # start and end are in the same chapter of the same book
            if self.start.chapter == self.end.chapter:
                f = self.format('B C:V-v')
            
            # start and end are in different chapters of the same book
            else:
                f = self.format('B C:V - c:v')
        
        # start and end are in different books
        else:
            f = self. formatq('B C:V - b c:v')
        
        # return the formatted value
        return f