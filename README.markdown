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
    45
    >>> v1.format('B C:V')
    Romans 1:1
    >>> v1.to_string()
    45-1-1
    
    >>> v = bible.Verse('Romans 17:1')
    ...
    RangeError: There are not that many chapters in Romans
    
    >>> v = bible.Verse('Gen 1:50')
    ...
    RangeError: There is no verse 50 in Genesis 1
    
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

Django Forms
------------
We've added a few additional classes to make it easy for you to use the bible
module in your Django models. Here's how:

    from bible.djangoforms import VerseField
    
    class Scripture(models.Model):
        """Sample model class using the VerseField type from the bible module"""
        start_verse = VerseField()
        end_verse = VerseField()

Used in the Django admin, or in your own forms, this will let the user enter
a verse in plain English, and attempt to interpret it into a Verse object.
If an exception is thrown, it will be passed through to the form for the user
to fix it.

In the specific example above, given a model with start and end verses, a
Passage object could be created in your view by combining the two Verse objects:

    from bible import Passage
    from myproject.myapp.models import Scripture
    
    s = Scripture.objects.get(id=1)
    passage = Passage(s.start_verse, s.end_verse)

Which would then let you do something like this in your templates, assuming
you passed the passage variable in to the template context:

    {{ passage.smart_format }}

There are no template tags or filters built in to the module yet, but they
would definitely be a good addition (thinking specifically of implementing
a template filter for Verse.format() like the date filters built in to Django)