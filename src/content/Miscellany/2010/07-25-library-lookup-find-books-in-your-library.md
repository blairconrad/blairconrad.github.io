---
layout: post
title: Library Lookup - find books in your library
comments: true
tags: LibraryLookup
---
I'm an avid reader, but not an avid collector of objects, so I prefer to get books from the library. As you might imagine, I was initially thrilled to discover <a href="http://jonudell.net/udell/2006-01-30-further-adventures-in-lightweight-service-composition.html" />the greasemonkey user script</a> version  of <a href="http://jonudell.net/LibraryLookup.html">Jon Udell's LibraryLookup bookmarklet</a>. The ability to visit web pages about books and be told whether the books are in one's library is just incredibly convenient.

After a while, I wanted more - I wanted the script to work on more pages, and I wanted it to tell me if the book was in <i>any</i> of the three libraries that are available to me. So I reworked the script, modularizing it so it was easy to plug in additional libraries and source web pages. The resulting <a href="http://blairconrad.googlecode.com/svn/trunk/greasemonkey/XisbnLibraryLookupWpl.user.js">XISBN Library Lookup script</a> has served me well for years.

Recently, though, I've been using <a href="http://www.google.com/chrome/">Google Chrome</a> as my browser, and the user script (for whatever reason) doesn't work with Chrome's greasemonkey-to-extension translator. So, I've been "libary lookupless", and keenly felt the lack. 

<div class="images">
<a href="https://chrome.google.com/extensions/detail/lopekoojcojbmfpkbncnpihmjbbkdgdk"><img src="{static}/images/icon_128.png" border="0" alt="LibraryLookup icon" title="LibraryLookup" width="128" height="128" class="alignright size-full wp-image-571" /></a>
</div>

I figured this was an excellent opportunity to learn how to write Chrome extensions, and it was not too difficult.  The first incarnation of the new
<a href="https://chrome.google.com/extensions/detail/lopekoojcojbmfpkbncnpihmjbbkdgdk">Library Lookup Chrome Extension</a>

is available in the extension gallery. It's in its infancy, but it supports the these libraries:
<ul>
<li><a href="http://www.wpl.ca/">Waterloo Public Library</a></li>
<li><a href="http://kpl.org/">Kitchener Public Library</a></li>
<li><a href="http://rwl.library.on.ca/">Region of Waterloo Library</a></li>
</ul>

And it will start looking up libraries when you browse to a book's page at:
<ul>
<li><b>any site that has the ISBN in the URL</b>, including (but not limited to)
  <ul>
    <li><a href="http://www.amazon.com/">Amazon.com</a> (and country-specific variants),</li>
    <li><a href="http://www.chapters.indigo.ca/">Chapters/Indigo</a>, and</li>
    <li><a href="http://www.powells.com/">Powell's Books</a>,</li>
  </ul>
  <li><a href="http://www.goodreads.com/">Goodreads</a>,</li>
  <li><a href="http://www.allconsuming.net" />All Consuming</a>, and</li>
  <li><a href="http://www.librarything.com">LibraryThing</a></li>
</ul>

Try it now! Install the extension, visit <a href="http://www.amazon.ca/Time-Travelers-Wife-Audrey-Niffenegger/dp/0676976336">a book page</a>, and (if it's in the libraries) click on the handy "book found" page icon in the URL bar to see where your book is:

<div class="images">
<a href="{static}/images/found_tttw.png"><img src="{static}/images/found_tttw.png?w=300" alt="Library Lookup finds The Time Traveler&#039;s Wife" title="found_tttw" width="300" height="127" class="aligncenter size-medium wp-image-528" /></a>
</div>

