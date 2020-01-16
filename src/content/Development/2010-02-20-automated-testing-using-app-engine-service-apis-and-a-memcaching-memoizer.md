---
layout: post
title: Automated Testing using App Engine Service APIs (and a Memcaching Memoizer)
comments: true
tags: AppEngine, Decorators, Gael, LibraryHippo, Memcache, Python, Testing
---
I'm a fan of Test-driven development, and automated testing in general. As such, I’ve been trying ensure that the <a href="http://code.google.com/p/libraryhippo/">LibraryHippo</a> code has an adequate set of automated tests before deploying new versions.

<h2>Importing Google App Engine Modules</h2>  Unfortunately, testing code that relies on the <a title="Google App Engine" href="http://code.google.com/appengine/">Google App Engine</a> SDK is a little tricky, as I found when working with one of the LibraryHippo entities. There’s an entity called a Card, which extends `db.Model` and represents a user's library card.

  The Card definition is not entirely unlike this:

 

<pre><code class="python">class Card(db.Model):
    family = db.ReferenceProperty(Family)
    number = db.StringProperty()
    name = db.StringProperty()
    pin = db.StringProperty()
    library = db.ReferenceProperty(Library)

    def pin_is_valid(self):
        return self.pin != ''
</code></pre>

Unfortunately, testing this class isn't as straightforward as one would hope. Suppose I have this test file:



<pre><code class="python">from card import Card

def test_card_blank_pin_is_invalid():
    c = Card()
    c.pin = ''
    assert not c.pin_is_valid()
</code></pre>

It fails miserably, spewing out a string of import errors. Here's the tidied-up stack: 



<pre><code class="python">>  from card import Card
>  from google.appengine.ext import db
>  from google.appengine.api import datastore
>  from google.appengine.datastore import datastore_index
>  from google.appengine.api import validation
>  import yaml
E ImportError: No module named yaml
</code></pre>

Not so good. Fortunately, it’s not that hard to find out what needs to be done in order to make the imports work:



<pre><code class="python">import sys
import dev_appserver
sys.path = dev_appserver.EXTRA_PATHS + sys.path 

from card import Card

def test_card_blank_pin_is_invalid():
    c = Card()
    c.pin = ''
    assert not c.pin_is_valid()
</code></pre>

Now Python can find all the imports it needs. For a while this was good enough, since I wasn’t testing any code that hit the datastore or actually used any of the app Engine Service APIs.



<h2>Running the App Engine Service APIs</h2>

However, I recently found a need to use <a href="http://code.google.com/appengine/docs/python/memcache/">Memcache</a> to store partially-calculated results and decided (like everyone else) to write a memoizing decorator to do the job. There’s enough logic in my memoizer that I felt it needed an automated test. I tried this:



<pre><code class="python">import sys
import dev_appserver
sys.path = dev_appserver.EXTRA_PATHS + sys.path 

from google.appengine.api import memcache
from gael.memcache import *

def test_memoize_formats_string_key_using_kwargs():
    values = [1, 2]
    @memoize('hippo %(animal)s zebra', 100)
    def pop_it(animal):
        return values.pop()

    result = pop_it(animal='rabbit')
    assert 2 == result

    cached_value = memcache.get('hippo rabbit zebra')
    assert 2 == cached_value
</code></pre>

(`gael` is Google App Engine Library – my extension/utility package - as it grows and I gain experience, I may spin it out of LibraryHippo to be its own project.) Again, it failed miserably. Here’s a cleaned-up version of the failure:



<pre><code class="python">>  result = pop_it(animal='rabbit')
>  cached_result = google.appengine.api.memcache.get(key_value)
>  self._make_sync_call('memcache', 'Get', request, response)
>  return apiproxy.MakeSyncCall(service, call, request, response)
>  assert stub, 'No api proxy found for service "%s"' % service
E AssertionError: No api proxy found for service "memcache";
</code></pre>

This was puzzling. All the imports were in place, so why the failure? This time the answer was a little harder to find, but tenacious searching paid off, and I stumbled on a Google Group post&#160; called <a href="http://groups.google.com/group/google-appengine-python/browse_thread/thread/435b20de9b1e5cc4?fwc=1&pli=1">Unit tests / google apis without running the dev app server</a>. The author had actually done the work to figure out what initialization code had to be run in order to get have the Service APIs work. The solution relied on hard-coded paths to the App Engine imports, but it was obvious how to combine it with the path manipulation I used earlier to produce this:



<pre><code class="python">import sys

from dev_appserver import EXTRA_PATHS
sys.path = EXTRA_PATHS + sys.path 

from google.appengine.tools import dev_appserver
from google.appengine.tools.dev_appserver_main import ParseArguments
args, option_dict = ParseArguments(sys.argv) # Otherwise the option_dict isn't populated.
dev_appserver.SetupStubs('local', **option_dict)

from google.appengine.api import memcache
from gael.memcache import *

def test_memoize_formats_string_key_using_kwargs():
    values = [1, 2]
    @memoize('hippo %(animal)s zebra', 100)
    def pop_it(animal):
        return values.pop()

    result = pop_it(animal='rabbit')
    assert 2 == result

    cached_value = memcache.get('hippo rabbit zebra')
    assert 2 == cached_value
</code></pre>

There’s an awful lot of boilerplate here, so I tried to clean up the module, moving the App Engine setup into a new module in gael:



<pre><code class="python">import sys

def add_appsever_import_paths():
    from dev_appserver import EXTRA_PATHS
    sys.path = EXTRA_PATHS + sys.path 

def initialize_service_apis():
    from google.appengine.tools import dev_appserver

    from google.appengine.tools.dev_appserver_main import ParseArguments
    args, option_dict = ParseArguments(sys.argv) # Otherwise the option_dict isn't populated.
    dev_appserver.SetupStubs('local', **option_dict)
</code></pre>

Then the top of the test file becomes



<pre><code class="python">import gael.testing
gael.testing.add_appsever_import_paths()
gael.testing.initialize_service_apis()

from google.appengine.api import memcache
from gael.memcache import *

def test_memoize_formats_string_key_using_kwargs():
    ...
</code></pre>

<h2>The Decorator</h2>

In case anyone’s curious, here’s the <strong>memoize</strong> decorator I was testing. I needed something flexible, so it takes a <strong>key</strong> argument that can either be a format string or a callable. I’ve never cared for positional format arguments – not in Python, C#, Java, nor C/C++ – so both the format string and the callable use the <strong>**kwargs </strong>to construct the key. I’d prefer to use <a href="http://docs.python.org/library/stdtypes.html#str.format">str.format</a> instead of the `%` operator, but not until App Engine moves to Python 2.6+



<pre><code class="python">def memoize(key, seconds_to_keep=600):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if callable(key):
                key_value = key(args, kwargs)
            else:
                key_value = key % kwargs

            cached_result = google.appengine.api.memcache.get(key_value)
            if cached_result is not None:
                logging.debug('found ' + key_value)
                return cached_result
            logging.info('calling func to get '  + key_value)
            result = func(*args, **kwargs)
            google.appengine.api.memcache.set(key_value, result, seconds_to_keep)
            return result
        return wrapper
    return decorator
</code></pre>

<h2>Faking out Memcache - Unit Testing the Decorator</h2>

The astute among you are probably thinking that I could’ve saved myself a lot of trouble if I’d just faked out memcache and unit tested the decorator instead of trying to hook everything up for an integration test. That’s true, but at first I couldn’t figure out how to do that cleanly, and it was my first foray into memcache, so I didn’t mind working with the service directly.



Still, the unit testing approach would be better, so I looked at my decorator and rebuilt it to use a class rather than a function. It’s my first time doing this, and it’ll probably not be the last – I really like the separation between initialization and execution that the `__init__`/`__call__` methods give me; I think it makes things a lot easier to read.



<pre><code class="python">def memoize(key, seconds_to_keep=600):
    class memoize():
        def __init__(self, func):
            self.key = key
            self.seconds_to_keep=600
            self.func = func
            self.cache=google.appengine.api.memcache

        def __call__(self, *args, **kwargs):
            if callable(self.key):
                key_value = self.key(args, kwargs)
            else:
                key_value = self.key % kwargs

            cached_result = self.cache.get(key_value)
            if cached_result is not None:
                logging.debug('found ' + key_value)
                return cached_result
            logging.info('calling func to get '  + key_value)
            result = self.func(*args, **kwargs)

            self.cache.set(key_value, result, self.seconds_to_keep)
            return result

    return memoize
</code></pre>

Then the test can inject its own caching mechanism to override `self.cache`:



<pre><code class="python">class MyCache:
    def __init__(self):
        self.cache = {}

    def get(self, key):
        return self.cache.get(key, None)

    def set(self, key, value, *args):
        self.cache[key] = value

def test_memoize_formats_string_key_using_kwargs():
    values = [1, 2]
    @memoize('hippo %(animal)s zebra', 100)
    def pop_it(animal):
        return values.pop()

    cache = MyCache()
    pop_it.cache = cache
    result = pop_it(animal='rabbit')
    assert 2 == result

    cached_value = cache.get('hippo rabbit zebra')
    assert 2 == cached_value
</code></pre>

And that's it. Now I have a unit-tested implementation of my memoizer and two new helpers in my extension library.


