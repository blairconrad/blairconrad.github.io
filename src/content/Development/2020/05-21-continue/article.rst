LibraryHippo 2020 - Recap and decision
######################################

:tags: LibraryHippo, flask
:series: LibraryHippo 2020

In each of last six articles I've satisfied one of the high-risk requirements I
had for moving LibraryHippo to the Flask framework, with the goal of hosting it
on Heroku. This leaves three "softer" requirements open, which I'll address
here.

(Aside: It feels a little weird working on this conversion while my local
libraries (and many others across the world) are closed due to the 2019–2020
coronavirus pandemic. I'm unable to take books out or put them on hold for
testing purposes, and it's not clear when the libraries will reopen. And maybe
I'll be reluctant to borrow library materials for a while after they do open.
Still, I'm hopeful that the libraries will return to normal, and in the meantime
this is a fun project, so I might as well continue the series.)

Remaining requirements
======================

Custom domains
--------------

All levels of Heroku plans support custom domain names. They don't offer free
SSL , but LibraryHippo's been getting along well enough without SSL to this
point, so I might as well continue. And it looks like
`Cloudflare <https://www.cloudflare.com/en-ca/ssl/>`_ offers SSL for free, so
that may be an option in the future.

Job queues
----------

I'd used job queues on Google App Engine because each job's execution time was
capped at 30 seconds or so. It wasn't always possible to check even all the
cards for a single family in that time, so each card check was queued
separately. I've simulated a long-running job on Heroku with no problem, so the
job queue probably isn't necessary.

Cheap hosting
-------------

I don't intend to make any money with LibraryHippo, and while I enjoy it, I
don't want to pour hundreds (or even several tens) of dollars into it every
year. Everything I've tried so far has been done on a Heroku free dyno, and it
looks like it'll continue to meet my needs.

Next steps
==========

I feel good about meeting my requirements, so I'm going to continue converting the
application. Part of this will be fleshing out the skeleton that's there now;
for example, the library site scraping is nowhere near as robust as the current
LibraryHippo, and the site looks *terrible*. The remaining work will be adding
the features and underpinnings that are missing, such as:

* family management
* card management
* automated tests on the backend
* migrating users from the old application

Some of these steps may warrant a blog post, and some might not. We'll see how
it goes.