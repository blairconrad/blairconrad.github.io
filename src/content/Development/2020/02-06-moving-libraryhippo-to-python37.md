---
title: LibraryHippo 2020 - Motivation and Plan
tags: LibraryHippo, flask, AppEngine, heroku
series: LibraryHippo 2020
---

For some years, I've run a hobby project, open to all, but mostly used by a few
of my friends and family, called [LibraryHippo](http://libraryhippo.com/). I
find it useful, and for a long time, it was a joy to work on.

Lately, the project's not much fun. I've had the urge to make small tweaks or
add the odd feature, but I haven't bothered. Whenever I'm tempted to, there've
been a few speedbumps:

1. it's written in Python 2.7, which I'm trying to leave behind, and
1. it's running on Google App Engine

I'm grateful to Google for providing a free tier of App Engine for projects such
as mine to run on, and I've benefitted a lot from it, but it's not without its
downsides:

1. many of the services have custom interfaces, that I only use there, so they
   fade from my memory, and
1. it seems every time I come back to the project, I have to update my SDK to
   even work with LibraryHippo, and sometimes learn new commands to deploy or
   monitor the service

Since Python 2.7 is now unsupported, I'm looking to upgrade to 3.7. App Engine
documentation now suggests writing the application in
[Flask](https://palletsprojects.com/p/flask/), rather than the older framework.
The project seems well-regarded, so I read some documentation and looked at
Miguel Grinberg's amazing
[The Flask Mega-Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world),
(which I highly recommend: it's eminently readable, obviously well-researched,
and espouses good overall development practices), and decided to give that a
try.

I figured that since I'm doing a near-complete rewrite anyhow (some of the core
code should survive), it might be time to explore different hosting options,
making use of commodity databases, authentication, queuing, etc.

After a little searching, it looks as if [Heroku](https://heroku.com) might be
the platform that meets my needs, which are:

1. web app hosting
1. a small (perhaps a few MB) persistent datastore
1. scheduled jobs
1. authentication via social accounts
1. sending e-mail
1. free, or nearly so; as I said, this is a hobby project, and I'm not willing
   to dump several tens of dollars into it every month
1. **Update 2020-02-11:** scraping library websites on users' behalf

I've other requirements, but these aren't likely to be deal-breakers:

1. custom domain name
1. job queues

Over the next few posts, I'm going to pick high-risk requirements from the above
list, and attempt to satisfy them via a Flask web application running on
Heroku's free tier. If I can satisfy (in the most rudimentary way) these
requirements, I'll pursue a full conversion.

I'll assign issues and pull requests that I make for this work to the
[LibraryHippo 2020](https://github.com/LibraryHippo/LibraryHippo/milestone/1)
milestone.

Hopefully the series will serve as entertainment or education for you, and a
useful reference for me when I wonder how or why I did something.