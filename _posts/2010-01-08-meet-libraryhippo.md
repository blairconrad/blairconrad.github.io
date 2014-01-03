---
layout: post
title: Meet LibraryHippo
tags:
    - LibraryHippo
---
I enjoy <a href="http://www.goodreads.com/user/show/1066544">reading</a> and using my local libraries. My wife and I have four library cards between us - one each for the <a href="http://www.wpl.ca/">Waterloo Public Library</a>, one for the <a href="http://kpl.org/">Kitchener Public Library</a>, and one for the <a href="http://www.regionofwaterloo.canlib.ca/">Region of Waterloo Library</a>. Using our cards, we were able to find all kinds of books to read and DVDs to watch, but organizing our borrowing was a little annoying, since:
<ul>
	<li>we had to log into four different library accounts to get an overview of our current borrowings and holds,</li>
	<li>each  account had a long, hard-to-remember ID, and</li>
	<li>the library would send e-mail when items were overdue, not in time to take them back.</li>
</ul>
I'd been using <a href="http://www.libraryelf.com/">Library Elf</a> to manage our cards, but they'd recently moved to a for-pay model, so I combined a sense of frugality with the desire to build something using a new technology and created <a href="http://libraryhippo.appspot.com/">LibraryHippo</a>, a <a href="http://code.google.com/appengine/">Google App Engine</a>-powered web application that takes care of my library cards.

<a title="Visit LibraryHippo" href="http://libraryhippo.appspot.com/"><img title="LibraryHippo logo" src="{{ site.image_dir }}/libraryhippo-logo.png" alt="LibraryHippo logo" width="161" height="115" /></a>

LibraryHippo:
<ul>
	<li>manages multiple cards per family</li>
	<li>shows a comprehensive overview of a family's current library status</li>
	<li>sends e-mail every morning if
<ul>
	<li>a family has items that are nearly due</li>
	<li>there are items ready to be picked up, or</li>
	<li>there's a problem checking an account</li>
</ul>
</li>
</ul>
Feel free to check out the <a href="http://code.google.com/p/libraryhippo/">project, hosted on Google Code.</a> A fair number of my future posts will talk about the adventures I've had implementing and improving LibraryHippo.
