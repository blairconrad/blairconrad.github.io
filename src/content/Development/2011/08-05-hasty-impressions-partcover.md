---
layout: post
title: Hasty Impressions&#58; PartCover
comments: true
tags: .NET, coverage, HastyImpressions, OpenCover, PartCover, Testing
series: .NET Coverage Tools
---

<h2>Technical stuff</h2>
PartCover has a GUI runner as well as a command-line mode. It integrates with Isolator, but doesn't offer any help for those wanting to profile IIS-hosted applications.
There are some XSL files provided that allow one to generate HTML reports, but probably the better way is to use <a href="http://www.palmmedia.de/Net/ReportGenerator">ReportGenerator</a> to make HTML or XML reports. 
PartCover claims to be auto-deployable, but I did not try this.

<h2>Project Concerns</h2>
The hardest thing about working with PartCover is learning about PartCover - finding definitive information about the project's state is quite difficult. Searching with Google finds <a href="http://sourceforge.net/projects/partcover/">the SourceForge project</a> which contains a note to see latest news on the <a href="http://partcover.blogspot.com">PartCover blog</a>, which <b>hasn't been updated</b> since 17 June 2009. Back at SourceForge, you can download a readme written by Shaun Wilde, which says that he's the last active developer and has <b>moved development</b> to <a href="http://github.com/sawilde/partcover.net4">a GitHub project</a>.

<!--more-->

At last! A project with recent (26 June 2011) updates. Unfortunately, my trials did not end here. I tried a number of versions, each with their own quirks. Unfortunately, I did not keep as careful track of which version had which problem as I should, and can't say which version (from either GitHub or SourceForge) had which problems, but I can describe the problems.

At first I thought things were working really well, but then noticed that I had abnormally high coverage levels on my projects - one legacy project that I knew had about 5% coverage was registering as over 20%! 
I looked at one assembly's summary and found 6 classes with 0% coverage and one with 80%, and the assembly was registering an 80%. It turns out that <b>completely uncovered classes were not counting against the total</b>.

I tried other versions, with either the same results, or failures to run altogether. Ultimately, I gave up.
<h2>A Successor</h2>
It turns out that PartCover has a successor of sorts - Shaun Wilde, the last surviving maintainer of PartCover, has started his own coverage tool - <a href="https://github.com/sawilde/opencover">OpenCover</a>. It already seems be a viable PartCover replacement, and is in active development, so I'll be checking it out as a free, non-IDE-integrated coverage tool.

<h2>Conclusion</h2>
<strong>Pros:</strong>
<ul>
	<li>free!</li>
	<li>XML/HTML via ReportGenerator</li>
	<li>report merging via ReportGenerator</li>
	<li>Isolator support</li>
	<li>auto-deployable (reported)</li>
        <li>sequence point coverage</li>
</ul>
<strong>Cons:</strong>
<ul>
	<li>no IDE integration</li>
	<li>no special IIS support</li>
        <li>forked implementations, each with their own warts</li>
        <li>not quite abandoned, but not a lot of interest behind the project</li>
</ul>

Until I noticed the high coverage levels, I didn't mind PartCover. I figured its lack of price and its Isolator support made it a viable candidate. Unfortunately, the high coverage reports and other problems soured me on the deal, as did the lack of maintenance. I'm going to look at OpenCover instead.
