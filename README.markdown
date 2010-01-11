Python Classes for manipulating Bible references
------------------------------------------------
This module lets you interact with Bible verses and passages as Python
objects. It is useful for manipulating, comparing, formatting, and saving
Bible references.


Verse Object
------------
Attributes

* book (book of Bible: 1-66)
* chapter (chapter number)
* verse (verse number)

Methods

* format(format_string)  # outputs a nicely formatted string
* to_string()  # outputs a string in b-c-v format for saving to db


Passage Object
--------------
Attributes

* start (Verse object)
* end (Verse object)

Methods

* length()  # total number of verses included in passage
* format(format_string)  # outputs a nicely formatted string
* smart_format()  # outputs the most common human-readable string for a passage


Installation
------------
Clone this repository into a folder named "bible" in your Python path. Alternatively -
if you don't need the bleeding-edge updates and patches - you can use easy_install:

    easy_install bible

That should get you up and running without having to mess with cloning or anything.


Example Usage
-------------
Be sure you have this repository cloned into a folder named "bible" in your
Python path before trying any of the examples below. The examples below show
commands and output as entered using the Python interactive terminal.

Using Verse Objects:

    >>> import bible
    
    >>> v1 = bible.Verse('rom1:1')
    >>> v1.book
    44
    >>> v1.format('B C:V')
    Romans 1:1
    >>> v1.to_string()
    44-1-1
    
    >>> v = bible.Verse('Romans 17:1')
    ...
    Exception: There are not that many chapters in Romans
    
    >>> v = bible.Verse('Gen 1:50')
    ...
    Exception: There is no verse 50 in Genesis 1
    
    >>> v = bible.Verse('1-1-1')
    >>> v = bible.Verse('gen1:1')
    >>> v = bible.Verse('Genesis 1:1')
    >>> v = bible.Verse(1,1,1)

Using Passage Objects:
    
    >>> import bible
    
    >>> v1 = bible.Verse('rom1:1')
    >>> v2 = bible.Verse('rom1:8')
    >>> p = bible.Passage(v1,v2)
    >>> p.start.verse
    1
    >>> p.end.verse
    8
    >>> p.length()
    8
    >>> p.format('B C:V to b:c:v')
    Romans 1:1 to Romans 1:8
    >>> p.smart_format()
    Romans 1:1-8
        
    >>> p = bible.Passage(v1,v2)
    >>> p = bible.Passage(v1, 'Romans 1:8')
    >>> p = bible.Passage('rom1:1','rom1:8')
