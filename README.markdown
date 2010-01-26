Python Classes for manipulating Bible references
------------------------------------------------
Python classes for Bible Verse and Passage - useful for storing, comparing,
and formatting Bible references. Also includes Django form classes to make it
easy to add Bible references to your Django models.

Note that this module does not let you actually pull and display the text
of a Bible verse or passage - it is just for working with and displaying
the reference to the verses. Other tools and APIs can be used to grab and
display the actual verse text for a reference.

Including the translation in a Verse object is optional, but if used, the
omitted verses will be accounted for when interacting with the Verse or
Passage that it is in. Passages can not combine two Verse objects that are
not from the same translation. While any translation can be entered and
stored in the objects, the only ones with special data are: ESV, RSV, NIV,
NASB, NRSV, NCV, and LB.


Verse Object
------------
Attributes

* book (book of Bible: 1-66)
* chapter (chapter number)
* verse (verse number)
* translation (string: "ESV", "NASB", etc - or None)

Methods

* format(format_string)  # outputs a nicely formatted string
* __str__(self)  # normalized string output (for saving to database)


Passage Object
--------------
Attributes

* start (Verse object)
* end (Verse object)

Methods

* format(format_string)  # outputs a nicely formatted string
* smart_format()  # outputs the most common human-readable string for a passage
* __len__(self)  # total number of verses included in passage
* __str__(self)  # normalized string output (for saving to database)
* __contains__(self, verse) # checks to see if a Verse is included in the Passage


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
    >>> str(v1)
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
    >>> len(p)
    8
    >>> Verse('rom1:4') in p
    True
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