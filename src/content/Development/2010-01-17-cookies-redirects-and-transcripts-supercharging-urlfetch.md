---
layout: post
title: Cookies, Redirects, and Transcripts - Supercharging urlfetch
comments: true
tags: AppEngine, Development, LibraryHippo, Python
---
<p><a href="http://libraryhippo.appspot.com/">LibraryHippo</a>'s main function is fetching current library account status for patrons. Since I have no special relationship with any of the libraries involved, LibraryHippo <a href="http://en.wikipedia.org/wiki/Web_scraping">web scrapes</a> the libraries' web interfaces.</p>

<p>The library websites issue cookies and redirects, so I needed to do something to augment the <a href="http://code.google.com/appengine/docs/python/urlfetch/">URL Fetch Python API</a>. 
I wrote a utility class that worked with the urllib2 interface, but that didn't allow me to set the `deadline` argument, and I wanted to increase its value to 10 seconds. I resigned myself to wiring up a version that used urlfetch, when I found  <a href="http://everydayscripting.blogspot.com/2009/08/google-app-engine-cookie-handling-with.html">Scott Hillman's URLOpener</a>, which uses <a href="http://docs.python.org/library/cookielib.html">cookielib</a> to follow redirects and handle any cookies met along the way.</p>
<p>URLOpener looked like it would work for me, with a few tweaks - it didn't support relative URLs in redirects, it doesn't allow one to specify headers in requests, and it lacked one feature that I really wanted - a <em>transcript</em>.</p>
<h4 id="why_a_transcript">Why a transcript?</h4>
<p>The libraries don't provide a spec for their output, so I built the web scraper by trial and error, sometimes putting books on hold or taking them out just to get test data. Every once in a while something comes up that I haven't coded for and the application breaks. In these cases, I can't rely on the problem being reproducible, since the patron could've returned (or picked up) the item whose record was troublesome or some other library state might've changed. I need to know what the web site looked like when the problem occurred, and since the ultimate cause might be several pages back, I need a history.</p>
<p>I started adding a transcript feature to the URLOpener - recording every request and response including headers. As I worked, I worried about two things:
</p>

* the `fetch` logic was becoming convoluted, and</li>
* the approach was inflexible - what if later I didn't want to follow redirects, or to keep a transcript?


<h4 id="decorators_to_the_rescue">Decorators to the rescue</h4>
<p>I decided to separate each bit of functionality - following redirects, tracking cookies, and keeping a transcript - into its own <a href="http://en.wikipedia.org/wiki/Decorator_pattern">decorator</a>, to be applied as needed. First  I teased out the code that followed redirects, with my change to allow relative URLs:</p>

<pre><code class="python">class RedirectFollower():
    def __init__(self, fetcher):
        self.fetcher = fetcher

    def __call__(self, url, payload=None, method='GET', headers={},
                 allow_truncated=False, follow_redirects=False, deadline=None):
        while True:
            response = self.fetcher(url, payload, method, headers,
                                    allow_truncated, False, deadline)
            new_url = response.headers.get('location')
            if new_url:
                # Join the URLs in case the new location is relative
                url = urlparse.urljoin(url, new_url)

                # Next request should be a get, payload needed
                method = 'GET'
                payload = None
            else:
                break

        return response</code></pre>

<p>After that, the cookie-handling code was easy to put in its own class:</p>

<pre><code class="python">class CookieHandler():
    def __init__(self, fetcher):
        self.fetcher = fetcher
        self.cookie_jar = Cookie.SimpleCookie()

    def __call__(self, url, payload=None, method='GET', headers={},
                 allow_truncated=False, follow_redirects=True, deadline=None):
            headers['Cookie'] = self._make_cookie_header()
            response = self.fetcher(url, payload, method, headers,
                                    allow_truncated, follow_redirects, deadline)
            self.cookie_jar.load(response.headers.get('set-cookie', ''))
            return response

    def _make_cookie_header(self):
        cookieHeader = ""
        for value in self.cookie_jar.values():
            cookieHeader += "%s=%s; " % (value.key, value.value)
        return cookieHeader</code></pre>

<p>Now I had the `URLOpener` functionality back, just by creating an object like so:</p>

<pre><code class="python">fetch = RedirectFollower(CookieHandler(urlfetch.fetch))</code></pre>

<h4 id="implementing_transcripts">Implementing transcripts</h4>
I still needed one more decorator - the transcriber.


<pre><code class="python">class Transcriber():
    def __init__(self, fetcher):
        self.fetcher = fetcher
        self. transactions = []

    def __call__(self, url, payload=None, method='GET', headers={},
                 allow_truncated=False, follow_redirects=True, deadline=None):
        self.transactions.append(Transcriber._Request(vars()))
        response = self.fetcher(url, payload, method, headers,
                                    allow_truncated, follow_redirects, deadline)
        self.transactions.append(Transcriber._Response(response))
        return response

    class _Request:
        def __init__(self, values):
            self.values = dict((key, values[key])
                               for key in ('url', 'method', 'payload', 'headers'))
            self.values['time'] = datetime.datetime.now()

        def __str__(self):
            return '''Request at %(time)s:
  url = %(url)s
  method = %(method)s
  payload = %(payload)s
  headers = %(headers)s''' % self.values

    class _Response:
        def __init__(self, values):
            self.values = dict(status_code=values.status_code,
                               headers=values.headers,
                               content=values.content,
                               time=datetime.datetime.now())

        def __str__(self):
            return '''Response at %(time)s:
  status_code = %(status_code)d
  headers = %(headers)s
  content = %(content)s''' % self.values</code></pre>


<p>To record all my transactions, all I have to do is wrap my fetcher one more time. When something goes wrong, I can examine the whole chain of calls and have a better shot at fixing the scraper.</p>

<pre><code class="python">fetch = Transcriber(RedirectFollower(CookieHandler(urlfetch.fetch)))
response = fetch(patron_account_url)
try:
    process(response)
except:
    logging.error('error checking account for ' + patron, exc_info=True)
    for action in fetch.transactions:
            logging.debug(action)</code></pre>

<h4 id="extra_fine_logging_without_rewriting_fetch">Extra-fine logging without rewriting fetch</h4>
The exercise of transforming `URLOpener` into a series of decorators may seem like just that, an exercise that doesn't provide real value, but provides a powerful debugging tool for your other decorators. By moving the `Transcriber` to the inside of the chain of decorators, you can see each fetch that's made due to a redirect, and which cookies are set when:

<pre><code class="python">fetch = RedirectFollower(CookieHandler(Transcriber(urlfetch.fetch)))</code></pre>

<p>The only trick is that the `Transcriber.transactions` attribute isn't available from the outermost decorator. This is easily solved by extracting a base class and having it delegate to the wrapped item.</p>

<pre><code class="python">class _BaseWrapper:
    def __init__(self, fetcher):
        self.fetcher = fetcher

    def __getattr__(self, name):
        return getattr(self.fetcher, name)</code></pre>

<p>Then the other decorators extend `_BaseWrapper`, either losing their `__init__` or having them modified. For example, `CookieHandler` becomes:</p>

<pre><code class="python">class CookieHandler(_BaseWrapper):
    def __init__(self, fetcher):
        _BaseWrapper.__init__(self, fetcher)
        self.cookie_jar = Cookie.SimpleCookie()
...</code></pre>

<p>And then the following code works, and helped me diagnose a small bug I'd originally had in my `RedirectFollower`. As a bonus, if I ever need to get at `CookieHandler.cookie_jar`, it's right there too.</p>
<pre><code class="python">fetch = RedirectFollower(CookieHandler(Transcriber(urlfetch.fetch)))
fetch(patron_account_url)
for action in fetch.transactions:
    logging.debug(action)</code></pre>


