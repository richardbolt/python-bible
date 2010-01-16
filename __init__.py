import re
import string
import data

# regular expressions for matching a valid normalized verse string
verse_re = re.compile(r'^\d{1,2}-\d{1,3}-\d{1,3}(-[a-zA-Z]{2,})?$')

# regular expressions for identifying book, and chapter:verse references
book_re = re.compile(r'^\d*[a-zA-Z ]*')
ref_re = re.compile(r'\d{1,3}:\d{1,3}')
translation_re = re.compile(r'[a-zA-Z]{2,}$')

class RangeError(Exception):
    """Exception class for books, verses, and chapters out of range"""
    pass
    
class Verse:
    """Class to represent a Bible reference (book, chapter, and verse)"""
    
    def __init__(self, *args):
        """Create a new Verse object - accepts several different inputs:
        
        Examples: book = 46
                  chapter = 2
                  verse = 1
                  Verse(book, chapter, verse)
                  
                  normalized_string = '46-2-1'
                  Verse(normalized_string)
                  
                  unformatted_string = '1 Cor 12:1'
                  unformatted_string = '1cor12:1'
                  unformatted_string = '1c 12:1'
                  Verse(unformatted_string)"""
        
        # if we got 3 or 4 values, let's assume they are book, chapter, verse, translation)
        if len(args) >= 3:
            self.book = args[0]
            self.chapter = args[1]
            self.verse = args[2]
            if len(args) == 4:
                self.translation = args[3]
            
        # if we only got one value, lets try to figure it out
        elif len(args) == 1:
            
            # maybe we got a normalized b-c-v(-t) string
            try:
                
                # check to make sure we have a valid verse string
                if not verse_re.search(args[0]):
                    raise Exception('String should be in normalized b-c-v(-t) format.')

                # extract the parts from the string
                parts = args[0].split('-')
                self.book, self.chapter, self.verse = map(int, parts[:3])
                if len(parts) > 3:
                    self.translation = parts[3]
            
            # if not, let's try to extract the values
            except:

                # find the book reference
                try:
                    b = book_re.search(args[0]).group(0)
                except:
                    raise RangeError("We can't find that book of the Bible: %s" % (args[0]))

                # find the chapter:verse reference
                try:
                    ref = ref_re.search(args[0]).group(0)
                except:
                    raise Exception("We can't make sense of your chapter:verse reference")

                # find the translation, if provided
                try:
                    self.translation = translation_re.search(args[0]).group(0).upper()
                    self.bible = data.bible_data(self.translation)
                except:
                    self.bible = data.bible_data()

                # try to find the book listed as a book name or abbreviation
                b = b.rstrip('.').lower().strip()
                for i, book in enumerate(self.bible):
                    if book['name'].lower() == b:
                        found = i + 1
                        break
                    else:
                        for abbr in book['abbrs']:
                            if abbr == b:
                                found = i + 1
                                break
                try:
                    self.book = found
                except:
                    raise RangeError("We can't find that book of the Bible!: " + b)

                # extract chapter and verse from ref
                self.chapter, self.verse = map(int, ref.split(':'))
        
        # check to see if the chapter is in range for the given book
        try:
            verse_count = self.bible[self.book - 1]['verse_counts'][self.chapter - 1]
        except:
            raise RangeError("There are not that many chapters in" + self.bible[self.book - 1]['name'])

        # check to see if the verse is in range for the given chapter
        if verse_count < self.verse:
            raise RangeError("There is no verse %s in %s %s" % (self.verse, self.bible[self.book - 1]['name'], self.chapter))
        
        # check to see if the specified verse is omitted
        try:
            omitted = self.verse in self.bible[self.book - 1]['omissions'][self.chapter-1]
            try:
                err = 'This verse is omitted from the %s translation.' % self.translation
            except:
                err = 'This verse is omitted from all modern translations.'
        except:
            omitted = False
        if omitted:
            raise RangeError(err)
            
    def __unicode__(self):
        return self.format()
    
    def format(self, val="B C:V"):
        """Return a formatted string to represent the verse
        Letters are substituted for verse attributes, like date formatting"""
        
        # create blank string to hold output
        f = ""
        
        # iterate over letters in val string passed in to method
        for c in val:
            f += _format_char(self, c)
        
        # return the formatted value
        return f.strip()
    
    def to_string(self):
        """Casts a verse object into a normalized string
        This is especially useful for saving to a database"""
        
        # set the base string to book, chapter, and verse number
        v = "%s-%s-%s" % (str(self.book), str(self.chapter), str(self.verse))
        
        # try to add the version to the string - if not set, just return the base string
        try:
            return v + '-' + str(self.translation)
        except:
            return v
        

class Passage:
    """A passage of scripture with start and end verses"""
    
    def __init__(self, start, end):
        """Create a new Passage object - accepts Verse objects or any
        string inputs that can process into valid Verse objects
        
        Examples: v1 = Verse('Rom. 1:1')
                  v2 = Verse('Rom. 1:8')
                  Passage(v1, v2)
                  
                  Passage('Rom. 1:1', 'Rom. 1:8')"""
        
        # if the args passed were objects, add them to the Passage
        # directly, otherwise try to interpret them as strings  
        if type(start).__name__ == 'instance':
            self.start = start
        else:
            self.start = Verse(start)
        if type(end).__name__ == 'instance':
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
                count = self.bible[self.start.book-1]['verse_counts'][self.start.chapter - 1] - self.start.verse + 1
                
                # add number of verses in whole chapters between start and end
                for chapter in range(self.start.chapter + 1, self.end.chapter):
                    count += self.bible[self.start.book - 1]['verse_counts'][chapter - 1]
                
                # add the number of verses in the end chapter
                count += self.end.verse
        
        # start and end are in different books
        else:
            
            # get number of verses in first chapter of start book
            count = self.bible[self.start.book - 1]['verse_counts'][self.start.chapter - 1] - self.start.verse + 1
            
            # add number of verses in whole chapters of start book
            for chapter in range(self.start.chapter, len(self.bible[self.start.book - 1]['verse_counts'])):
                count += self.bible[self.start.book - 1]['verse_counts'][chapter]
            
            # add total number of verses in whole books between start and end
            for book in range(self.start.book + 1, self.end.book):
                for chapter_count in self.bible[book - 1]['verse_counts']:
                    count += chapter_count
            
            # add number of verses in whole chapters of end book
            for chapter in range(1, self.end.chapter):
                count += self.bible[self.end.book - 1]['verse_counts'][chapter - 1]
            
            # get the number of verses in last chapter of end book
            count += self.end.verse
        
        # return the count
        return count
    
    def format(self, val="B C:V - b c:v"):
        """Return a formatted string to represent the passage
        Letters are substituted for verse attributes, like date formatting
        Lowercase letters (a, b, c, and v) refer to end verse reference
        The letter P inserts the smart_format() string for the passage"""
        
        # create blank string to hold output
        f = ""
        
        # iterate over letters in val string passed in to method
        for c in val:
            if c == "P":
                f += self.smart_format()
            elif c.isupper():
                f += _format_char(self.start, c)
            else:
                f += _format_char(self.end, c)
        
        # return formatted string
        return f.strip()
    
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
            f = self. format('B C:V - b c:v')
        
        # return the formatted value
        return f


def _format_char(verse, char):
    """return a string for the part of a verse represented by a
    formatting char:
    
    A - Book abbreviation (e.g. "Gen", "Rom")
    B - Full book name (e.g. "Genesis", "Romans")
    C - Chapter number
    V - Verse number
    T - Translation"""
    
    # use uppercase letter for comparison
    c = char.upper()
    
    # replace vals for start verse
    if c == "B":
        return verse.bible[verse.book-1]['name']
    elif c == "A":
        return verse.bible[verse.book-1]['abbrs'][0].title()
    elif c == "C":
        return str(verse.chapter)
    elif c == "V":
        return str(verse.verse)
    elif c == "T":
        try:
            return str(verse.translation)
        except:
            return ""
    else:
        return char