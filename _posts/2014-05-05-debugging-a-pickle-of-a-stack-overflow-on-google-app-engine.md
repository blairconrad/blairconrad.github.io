---
layout: post
title: "Debugging a Pickle of a Stack Overflow on Google App Engine" 
comments: true
tags:
        - pickle
        - AppEngine
        - LibraryHippo
        - Python
---

A few days ago, a user e-mailed me a bug report for
[LibraryHippo][LibraryHippo]. For the previous 55 days, she'd been
receiving the same (erroneous) morning e-mail about what library
materials she had due. However, when she checked her family's account
summary on the web page, it was correct.

> (The exact cause of the problem won't be of interest to many people,
> but I thought the way it presented, and how I diagnosed it, might
> help someone out. Read on!)

I checked the logs, and sure enough, there was an error. Sort of like this:

<pre>
I 2014-04-28 14:10:43.429 checking [patron name redacted] Waterloo
I 2014-04-28 14:10:47.550 saving checked card for [patron name redacted]
<b>E 2014-04-28 14:10:51.061 Failed to save checked card. Continuing.</b>
Traceback (most recent call last):
  File "/base/data/home/apps/s~libraryhippo27/1.368776574735783966/libraryhippo.py", line 380, in save_checked_card
    checked_card.payload = card_status
  File "/base/data/home/runtimes/python27/python27_lib/versions/1/google/appengine/ext/db/__init__.py", line 614, in __set__
    value = self.validate(value)
  File "/base/data/home/apps/s~libraryhippo27/1.368776574735783966/gael/objectproperty.py", line 11, in validate
    result = pickle.dumps(value)
  File "/base/data/home/runtimes/python27/python27_dist/lib/python2.7/pickle.py", line 1374, in dumps
    Pickler(file, protocol).dump(obj)
  File "/base/data/home/runtimes/python27/python27_dist/lib/python2.7/pickle.py", line 224, in dump
    self.save(obj)
  File "/base/data/home/runtimes/python27/python27_dist/lib/python2.7/pickle.py", line 286, in save
    f(self, obj) # Call unbound method with explicit self
  File "/base/data/home/runtimes/python27/python27_dist/lib/python2.7/pickle.py", line 725, in save_inst
    save(stuff)
  File "/base/data/home/runtimes/python27/python27_dist/lib/python2.7/pickle.py", line 286, in save
    f(self, obj) # Call unbound method with explicit self

<b>[about 80 lines of stack trace elided]</b>

  File "/base/data/home/runtimes/python27/python27_dist/lib/python2.7/pickle.py", line 663, in _batch_setitems
    save(v)
  File "/base/data/home/runtimes/python27/python27_dist/lib/python2.7/pickle.py", line 286, in save
    f(self, obj) # Call unbound method with explicit self
  File "/base/data/home/runtimes/python27/python27_dist/lib/python2.7/pickle.py", line 725, in save_inst
    save(stuff)
  File "/base/data/home/runtimes/python27/python27_dist/lib/python2.7/pickle.py", line 286, in save
    f(self, obj) # Call unbound method with explicit self
  File "/base/data/home/runtimes/python27/python27_dist/lib/python2.7/pickle.py", line 649, in save_dict
    self._batch_setitems(obj.iteritems())
  File "/base/data/home/runtimes/python27/python27_dist/...(length 98720)
I 2014-04-28 14:10:51.275 Saved; key: __appstats__:043300, part: 190 bytes, full: 65479 bytes, overhead: 0.004 + 0.005; link: http://libraryhippo27.appspot.com/_ah/stats/details?time=1398708643356
</pre>

Whenever LibraryHippo checks a patron's library card, it saves the
results to the datastore to be used to construct the next day's
e-mails, but an inability to save doesn't keep the results from being
displayed on the web page. So that part made sense. 

The next step was to figure out what was going wrong with the save.
The logs indicated that [pickle][pickle] was using more stack frames
than were available.


I try to debug it
-----------------

I added a copy of the offending card to my family's account on the live site. Same problem.
Then I fired up the dev environment at home and did the same thing. Everything worked like a charm.

That was unexpected. So, as a last resort, I started thinking.

Why so deep?
------------

The structure that was being pickled (`CardStatus`) was quite
flat. Here are the involved classes' definitions. Unless noted
otherwise, everything is a string or datetime:

<pre><code class="python">class CardStatus:
    def __init__(self, card, items=None, holds=None):

        self.library_name = card.library.name
        self.patron_name = card.name
        self.items = items or []  # Items
        self.holds = holds or []  # Holds
        self.info = []            # strings
        self.expires = datetime.date.max

class Thing():
    def __init__(self, library, card):

        self.library_name = library.name
        self.user = card.name
        self.title = ''
        self.author = ''
        self.url = ''
        self.status = ''
        self.status_notes = []    # strings

class Hold(Thing):
    def __init__(self, library, card):
        Thing.__init__(self, library, card)

        self.pickup = ''
        self.holds_url = ''
        self.expires = datetime.date.max

class Item(Thing):
    def __init__(self, library, card):
        Thing.__init__(self, library, card)

        self.items_url = ''</code></pre>

So, one level for the `CardStatus`, one for `Thing`, one for `Hold`
(or `Item`), one for a list, and one for the `status_notes` strings in
the list. That's 5 levels. And probably pickle encodes a `dict` in a
few of the of the complex types. Let's be generous and say 10 levels,
each of which take maybe 5 nested pickle functions. That's about
50. Plus however deep we are in the stack before the pickling
happens. That shouldn't be more than **100**.


How deep is too deep?
--------------------- 

Popular wisdom on the web seems to be to increase the recursion limit
when pickle runs into these kinds of problems. I was loath to do this,
as I'd be constantly worrying about what depth to allow and whether
it'd be enough and so on.

While I dithered over that, my wife called to me from the television
room, "Just set the limit higher. That should help your user for now
and it will give you more time to work on the problem."

So I did. I was worried that the App Engine runtime wouldn't _let_ me
change the recursion limit, so I used
[sys.getrecursionlimit][getrecursionlimit] to log the depth,
[sys.setrecursionlimit][setrecursionlimit], and
`sys.getrecursionlimit` again to verify.

Turns out that:

* The default recursion limit on App Engine's environment is **800**.
* You _can_ change the limit. I went up to **20000**.
* In the dev environment the limit is **1000**.

The higher limit on the production server fixed things. I relaxed a
little, and started thinking.

Maybe the 800/1000 difference accounted for things working at home,
but not in production. I used `sys.setrecursionlimit` to change the
limit at home, and reproduced the error. Huzzah! Now I could move more
quickly.

Inserting diagnostics into pickle
---------------------------------

Back to the question of why pickle was recursing so deeply. I don't
routinely debug Python, relying instead on the power of logging
statements. Thus, I decided to provide a custom pickler that did
normal pickling things, but that also, for every object pickled,
logged the stack depth, the object type, and its representation:


<pre><code class="python">import pickle
import logging
import traceback

class SpyingPickler(pickle.Pickler, object):
    def save(self, obj):
        logging.info("depth: %d, obj_type: %s, obj: %s",
                     len(traceback.extract_stack()),
                     type(obj), repr(obj))
        super(SpyingPickler, self).save(obj)</code></pre>

I ran this, and got reams of data. Scads and scads and scads, including what looked like to be large HTML documents. So I took out the `repr(obj)` and repeated. This was more manageable.


<pre>
&hellip;
depth: 176, obj_type: <class 'BeautifulSoup.NavigableString'>
depth: 179, obj_type: <type 'function'>
depth: 179, obj_type: <type 'tuple'>
depth: 182, obj_type: <type 'type'>
depth: 182, obj_type: <type 'type'>
depth: 182, obj_type: <type 'unicode'>
&hellip;
</pre>

Already we can see that we're quite deep in the stack, but the real
surprise was the `BeautifulSoup.NavigableString`. LibraryHippo uses
[BeautifulSoup][beautifulsoup] to scrape the libraries' web pages. A
[`NavigableString`][navigablestring] is basically a Unicode string
plus navigation. To support the navigation, the instance points at
what looks to be a DOM model of **the entire parsed HTML page**. That
explains the deep deep recursion.

The offending objects were in the `pickup` field of the `Hold`
class. A quick fix to ensure we're storing a plain string, and the
problem [was resolved][thefix].

What a difference
-----------------

Aside from the obvious effect of correct e-mails, I was curious to see what other differences this change made.

Before the fix, the serialization descended to a stack depth of
**892**, and produced a **546221**-byte blob.  After, the maximum
depth is **52**, and the blob size is **10779** bytes. So everyone
should benefit a little from lower resource usage and quicker
card-checking. Fortunately, LibraryHippo isn't popular enough to exceed
the free quotas, so I wasn't paying extra for compute or storage. Then
again, if I had been, maybe I would've noticed the problem before a user
did.

[LibraryHippo]: http://libraryhippo.com
[pickle]: https://docs.python.org/2/library/pickle.html
[getrecursionlimit]: https://docs.python.org/2/library/sys.html#sys.getrecursionlimit
[setrecursionlimit]: https://docs.python.org/2/library/sys.html#sys.setrecursionlimit
[picklesource]: http://hg.python.org/cpython/file/0f6bdc2b0e38/Lib/pickle.py
[beautifulsoup]: http://www.crummy.com/software/BeautifulSoup/
[navigablestring]: http://www.crummy.com/software/BeautifulSoup/bs4/doc/#navigablestring
[thefix]: https://code.google.com/p/libraryhippo/source/detail?r=fd04415d2009
