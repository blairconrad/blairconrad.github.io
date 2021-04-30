---
layout: post
title: Hasty Impressions: flake8 
comments: true
tags: python, flake8, HastyImpressions
---

A little while ago, I was fixing [a LibraryHippo issue][originalissue]
in an area of the code that didn't have very good unit test
coverage. As part of my fix, I moved one class from the main
`libraryhippo.py` file to its own file. I integration-tested the fix,
deployed the new version, and moved on.

A day or so later, I noticed that I'd
[broken a very important side effect][missingclock] of the
card-checking operation. The results of the check are cached and used
later when sending out notifications. Because we still want to deliver
a live report to users even if the caching fails, the failure is not
detectable from the web page.

Of course better test coverage would've picked this up, but it's the
sort of error that just as easily would've been caught in a compiled language such as
C#, or by a static analysis tool. So I decided to try out such a tool.

A few web searches later, and it looked like [flake8][flake8] was the
thing to try. It bundles together

* [PyFlakes](https://pypi.python.org/pypi/pyflakes)
* [pep8](https://pypi.python.org/pypi/pep8), and
* [mccabe](https://pypi.python.org/pypi/mccabe)

None of which I'd heard of before, (at least as packages&mdash;I'd
known of [PEP 8](http://legacy.python.org/dev/peps/pep-0008/)  for a
long time), but they claimed to do what I wanted. So I gave
flake8 a go.

## Initial impressions

Installation was as easy as running `pip install flake8`. It picked up
the missing dependencies automatically, and I was ready to go in seconds.

Too impatient to read any docs, I ran it:

<pre><code>LibraryHippo&gt; flake8
Usage: flake8 [options] input ...
flake8: error: input not specified
</code></pre>

A helpful error message. I reran, specifying the application directory
(`flake8 App`) and got&hellip; rather a lot of output. It looked
like this:

<pre><code>app\BeautifulSoup.py:100:1: E265 block comment should start with '# '
app\BeautifulSoup.py:107:1: E302 expected 2 blank lines, found 1
app\BeautifulSoup.py:114:1: E302 expected 2 blank lines, found 1
&vellip;
app\cardchecker.py:61:13: F841 local variable 'name' is assigned to but never used
app\cardchecker.py:63:80: E501 line too long (96 &gt; 79 characters)
app\cardchecker.py:71:37: F821 undefined name 'clock'
app\cardchecker.py:74:80: E501 line too long (84 &gt; 79 characters)
app\cardchecker.py:75:1: W391 blank line at end of file
&vellip;
</code></pre>

and so on. Success!

## Too many complaints!

Things seemed to be working, and it did identify the cause of my error
(`app\cardchecker.py:71:37: F821 undefined name 'clock'`), but it was
buried in way too much other information. 

flake8 reported **823** problems in my application (and that didn't
even include the test code). This is a common problem when running any
kind of analysis tool for the first time. Since we've not been running
a tight ship, there are all kinds of problems in the
code. Fortunately, like many tools of its ilk, flake8 lets us tailor
the problems that are reported. I had two immediate goals:

* ignore complaints about the library 
  [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/)
  (over half the complaints were from BeautifulSoup.py), and
* ignore (for now) less severe errors and style warnings

Now, how to do that?

## Command-line help

I hoped that the tool would give me useful help if I asked, and it
did:

<pre><code>LibraryHippo&gt;flake8  -h
Usage: flake8 [options] input ...

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -v, --verbose         print status messages, or debug with -vv
  -q, --quiet           report only file names, or nothing with -qq
  --first               show first occurrence of each error
  --exclude=patterns    exclude files or directories which match these comma
                        separated patterns (default:
                        .svn,CVS,.bzr,.hg,.git,__pycache__)
  --filename=patterns   when parsing directories, only check filenames
                        matching these comma separated patterns (default:
                        *.py)
  --select=errors       select errors and warnings (e.g. E,W6)
  --ignore=errors       skip errors and warnings (e.g. E4,W)
  --show-source         show source code for each error
  --show-pep8           show text of PEP 8 for each error (implies --first)
  --statistics          count errors and warnings
  --count               print total number of errors and warnings to standard
                        error and set exit code to 1 if total is not null
  --max-line-length=n   set maximum allowed line length (default: 79)
  --hang-closing        hang closing bracket instead of matching indentation
                        of opening bracket's line
  --format=format       set the error format [default|pylint|&lt;custom&gt;]
  --diff                report only lines changed according to the unified
                        diff received on STDIN
  -j JOBS, --jobs=JOBS  number of jobs to run simultaneously, or 'auto'
  --exit-zero           exit with code 0 even if there are errors
  --builtins=BUILTINS   define more built-ins, comma separated
  --doctests            check syntax of the doctests
  --max-complexity=MAX_COMPLEXITY
                        McCabe complexity threshold
  --install-hook        Install the appropriate hook for this repository.

  Testing Options:
    --benchmark         measure processing speed

  Configuration:
    The project options are read from the [flake8] section of the tox.ini
    file or the setup.cfg file located in any parent folder of the path(s)
    being processed.  Allowed options are: exclude, filename, select,
    ignore, max-line-length, hang-closing, count, format, quiet, show-
    pep8, show-source, statistics, verbose, jobs, builtins, doctests, max-
    complexity.

    --config=path       user config file location (default:
                        C:\PortableApps\Home\.flake8)
</code></pre>

Seems comprehensive. I bet a bunch of those would be quite handy
in time, but right now, it looked like I wanted `--select` to limit
the kinds of complaints. Based on the example, I figured I could use a
single letter to include a whole class of complaints. And it looked like
`--exclude` would keep flake8 from examining BeautifulSoup:

<pre><code>LibraryHippo&gt;flake8 App --select=F --exclude=BeautifulSoup.py
App\cardchecker.py:6:1: F401 'DeadlineExceededError' imported but unused
App\cardchecker.py:61:13: F841 local variable 'name' is assigned to but never used
App\cardchecker.py:71:37: F821 undefined name 'clock'
</code></pre>

There were complaints about other files, but the total count was down to
31, which was quite manageable. The "F" codes come from PyFlakes, and
don't necessarily mean "fatal" like I first thought. Some, such as
F841, are valid problems, but hardly catastrophic. Still, it was a
small matter to fix all the "F"s in the code. Later on, I went back,
expanding to changing the `--select` to `F,E` and eventually omitting
it altogther.

## Command-line arguments are so tedious

Always specifying options to ignore files or set maximum line lengths
(79 is just too short even for an editor taking up the left half of my
screen) can get old fast, so flake8 lets you put ever-repeated
settings in a file. As promised, the following `setup.cfg` file lets
me just run `flake8 App` and get the same results as above:

<pre><code class="ini">[flake8]
exclude = BeautifulSoup.py
select = F</code></pre>

## Handy extension: naming

It's possible to write extensions for flake8, and a number already
exist. In fact, mccabe looks to be implemented as an extension (and
maybe the others, I didn't check). On a lark, I went looking and found
the [pep8-naming][naming]
extension, which checks PEP 8 naming conventions (something
not fully covered by pep8, I guess). Installation via pip was simple
and now  
`flake8 --version` reports

<pre><code>2.2.2 (pep8: 1.5.7, pyflakes: 0.8.1, mccabe: 0.2.1, naming: 0.2.2)
CPython 2.7.2 on Windows</code></pre>

(And just running flake8 shows a whole bunch of "N8*"
complaints such as

<pre><code>App\wpl.py:227:17: N806 variable in function should be lowercase
App\gael\memcache.py:16:11: N801 class names should use CapWords convention
</code></pre>

But that's my problem to deal with.)

Writing new extensions doesn't look to be too difficult, if anyone
listening is interested in helping the tool spell-check my symbol
names (and maybe comments).

## Impressions

A very useful static analysis tool that is easy to set up, runs
quickly, and is configurable enough to start working on almost any
codebase. So far the complaint descriptions seem good, and I can
quickly resolve reported problems without consulting a manual. The
extension ecosystem provides even more power, if you need it.

### Will I Use It?

Absolutely, and you should too.

I'm so committed to it that I wrote a "deploy.bat" file that will only
deploy to Google App Engine if flake8 doesn't complain.


[flake8]: https://pypi.python.org/pypi/flake8
[naming]: https://pypi.python.org/pypi/pep8-naming
[missingclock]: https://github.com/LibraryHippo/LibraryHippo/issues/3
[originalissue]: https://github.com/LibraryHippo/LibraryHippo/pull/2
[naming]: https://pypi.python.org/pypi/pep8-naming
