---
layout: post
title: AutoTest.Net updated - now (and then) notices broken builds
tags:
    - .NET
    - AutoTest.Net
    - Testing
---
I received a useful comment on <a href="{% post_url 2011-07-29-hasty-impressions-dotcover-1-1 %}">Friday's post about AutoTest.Net</a>. In the wee hours of Saturday, <a href="http://codebetter.com/blogs/gregyoung/">Greg Young</a>, wrote to say

> It should detect broken builds without any problem. We have been running it daily for about 1.5 months.  
> Perhaps you could grab me via email and reproduce it?


Well, I wasn't going to pass up that offer. Off to GMail!

<table>
<tr><td>7:15</td><td>I grabbed him</td></tr>
<tr><td>7:20</td><td>he was making specific requests for additional information, the output of test runs through the console runner, and the like. </td></tr>
<tr><td>8:00</td><td>he had dived into the code to verify that things were working as they should, and asked for a sample project that exhibited the bug.</td></tr>
<tr><td>8:20</td><td>I sent the code</td></tr>
<tr><td>8:31</td><td>I e-mailed that <i>I'd accidentally sent a project that complied</i></td></tr>
<tr><td>8:34</td><td>Greg reproduced the problem</td></tr>
<tr><td>8:54</td><td>he sent me a replacement .zip file</td></tr>
<tr><td>9:04</td><td>it worked!</td></tr>
</table>

As soon as I broke the compilation, the monitor lit up, showing me which project failed and where:

<pre>
[Info] 'AutoTest.Console.ConsoleApplication' Preparing build(s) and test run(s)
[Info] 'AutoTest.Console.ConsoleApplication' Error: D:\bconrad\Documents\Source\BlogExamples\2010-11-autotest\BookFinder\BookFinder.Core\BookListViewModel.cs(50,17) CS1002: ; expected [D:\bconrad\Documents\Source\BlogExamples\2010-11-autotest\BookFinder\BookFinder.Core\BookFinder.Core.csproj]
[Info] 'AutoTest.Console.ConsoleApplication' Ran 1 build(s) (0 succeeded, 1 failed) and 0 test(s) (0 passed, 0 failed, 0 ignored)
</pre>

It turns out that the bug had already been fixed on trunk version of the code, but for some reason hadn't been built into the Windows installer. Turnaround time: 1 hour 49 minutes from my initial e-mail, and that included:
<ul>
<li>me drifting off to other tasks between e-mails, increasing delays</li>
<li>a session of trying to work around GMail hating the zip file I tried to send</li>
<li>a delay imposed by my having sent a bad test project</li>
</ul>
I'm sure those things added a good half hour to the required time.

Then he spent another 40 minutes on a non-existent problem that I reported. I'd left an older AutoTest.Net WinForms monitor running during the debugging, so when things finally settled down, I got a pair of toasts from Growl - one reporting build failures, and one reporting successful builds when there weren't any.
When I discovered that, Greg was already installing a new Growl for Windows to try it out. And he was very gracious about my error and his wasted time.

I'm hardly the first to point it out, but this is one of the great things about open software. It's great getting that kind of service so quickly. And on a weekend no less.

<h2>Will this encourage me to use AutoTest.Net</h2>
Sure. My primary complaint with it has been resolved. 
Moreover, I'd be even more inclined to see what comes of Mighty Moose, now that I see the dedication of the developers behind it.
