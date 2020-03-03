---
layout: post
title: Can you cover me&#63; Looking for a .NET coverage tool
comments: true
tags: .NET, coverage, IIS, Isolator, Testing, TypeMock
series: .NET Coverage Tools
excerpt: I'm looking for a .NET coverage tool to dazzle us with tales of test runs. Over the next little while, I'll look at a few candidates, summarize my findings, and hopefully come up with a winner. I look at dotCover, NCover,  PartCover, and OpenCover
---
Recently at the Day Job, my boss's boss has been on a "code confidence" kick. We've always done various levels of automated and manual unit, integration, issue, system, and regression testing, but he's looking to improve the process. Part of this push involves getting better at measuring which tests exercise what parts of the code. We want to know this for the usual reasons: we can identify gaps in our testing, or more likely find opportunities to cover some areas earlier in the testing cycle. It'd be nice to know that a particularly critical section of code has been adequately exercised by the per-build unit tests, without having to wait for nightly integration testing or wait even longer for a human to get their grubby mitts on it.

To that end, I'm looking for a .NET coverage tool to dazzle us with tales of test runs. Over the next little while, I'll look at a few candidates, summarize my findings, and hopefully come up with a winner.

<h2>Considerations</h2>
Here are some factors that will influence me. Some of these may be negotiable, if a candidate really shines in other areas.

<ul>
<li>We'd like to see coverage information in our build reports, so the tool should <b>run from the command line</b>.</li>
<li>It'd be easier to put the coverage info our our build reports if the <b>coverage reports were in XML</b>.</li>
<li>I really prefer a product that <b>has an auto-deploy</b>, so it can be bundled with the source tree and new developers or build servers just work. You may remember the pains I went to to <a href="{filename}../2010/06-06-auto-deploying-typemock-isolator-without-trashing-the-installation.md">auto-deploy TypeMock Isolator</a>.</li>
<li>While I'm on the subject, one of our products uses Isolator as its mocking framework, so the coverage tool should be able to <b>link with TypeMock Isolator</b>.</li>
<li>We have a web services layer, which will be exercised by unit tests, but if we could gather stats on the layer as it's being exercised by the client-facing portion, that would be gravy. To that end, it should be possible to <b>cover IIS</b>.</li>
<li>When I used TestDriven.NET + NCover a few years ago, I enjoyed being able to quickly see what my tests covered. This isn't a requirement of our current initiative, but <b>IDE integration</b> would be a bonus.</li>
<li><b>Price</b> is a factor. Money's available, but why spend if you don't have to? Or at least, why not pay less for an equivalent product.</li>
</ul>

 <h2>The Candidates</h2>
Googling has lead me to these candidates, which I'll be examining in the next little while:
<ul>
<li><a href="http://www.jetbrains.com/dotcover/">dotCover</a> (<a href="{filename}../2011/07-29-hasty-impressions-dotcover-1-1.md">my impression</a>)</li>
<li><a href="http://www.ncover.com/">NCover</a> (<a href="{filename}../2011/11-09-hasty-impressions-ncover.md">my impression</a>)</li>
<li><a href="http://sourceforge.net/projects/partcover/">PartCover</a> (<a href="{filename}../2011/08-05-hasty-impressions-partcover.md">my impression</a>)</li>
<li><a href="https://github.com/sawilde/opencover">OpenCover</a> (<a href="{filename}../2011/08-15-hasty-impressions-opencover.md">my impression</a>)</li>
</ul>

<b>Update</b>: <a href="{filename}../2011/12-15-best-all-around-net-coverage-tool-opencover.md">I picked one</a>.
 
