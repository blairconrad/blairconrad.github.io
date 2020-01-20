---
layout: post
title: Hasty Impressions&#58; OpenCover
comments: true
tags: .NET, coverage, OpenCover, HastyImpressions, Isolator, Testing, TypeMock
series: .NET Coverage Tools
---

<a href="https://github.com/sawilde/opencover">OpenCover</a> is developed by Shaun Wilde. He was a developer on (and is the only remaining maintainer of) PartCover. He's used what he learned working on PartCover to develop OpenCover, but OpenCover is a new implementation, not a port.

I tried OpenCover 1.0.514. Since I downloaded a couple weeks ago there have been 3 more releases, with the 1.0.606 release promising a big performance improvement.
<h2>The Cost</h2>
Free! And you can get the source.
<h2>VS integration</h2>
None that I can find.
<h2>Command Line Execution</h2>
Covering an application from the command line is <strong>easy</strong>, and reminiscent of using PartCover the same way. I used this command to see what code my BookFinder unit tests exercised:

<pre><code class="bat">OpenCover.Console.exe -arch:64 -register target:nunit-console.exe -targetargs:bin\debug\BookFinder.Tests.dll \
                      -output:..\..\opencover.xml -filter:+[BookFinder.Core]*</code></pre>
<!--more-->
Let's look at that.

* `-arch:64` - I'm running on a 64-bit system. I didn't get any results without this.
* `-register` - I'm auto-deploying OpenCover. More on that later.
* `-target:nunit-console.exe` - I like NUnit
* `-targetargs:bin\debug\BookFinder.Tests.dll` - arguments to NUnit to tell it what assembly to test, and how.
* `-output:..\..\opencover.xml` - where to put the coverage results. This file is not a report - it's intended for machines to read, not humans.
* `-filter:+[BookFinder.Core]*` - BookFinder.Core is the only assembly I was interested in - it holds the business logic.

<h2>GUI Runner</h2>
There isn't one, but I have to wonder if there won't be. Otherwise, why call the command line coverer <strong>OpenCover.Console.exe</strong>?

<h2>XML Report</h2>
OpenCover doesn't generate a human-readable report. Instead, you can postprocess the coverage output. <b><a href="http://www.palmmedia.de/Net/ReportGenerator">ReportGenerator</a> is the recommended tool</b>, and it works like a charm.


<pre><code class="bat">ReportGenerator.exe .\opencover.xml XmlReport Xml</code></pre>

generates an XML report in the `Xml` directory. The summary looks like this:

<pre><code class="xml">&lt;?xml version="1.0" encoding="utf-8"?&gt;
&lt;CoverageReport scope="Summary"&gt;
  &lt;Summary&gt;
    &lt;Generatedon&gt;2011-08-05-2011-08-05&lt;/Generatedon&gt;
    &lt;Parser&gt;OpenCoverParser&lt;/Parser&gt;
    &lt;Assemblies&gt;1&lt;/Assemblies&gt;
    &lt;Files&gt;5&lt;/Files&gt;
    &lt;Coverage&gt;71.6%&lt;/Coverage&gt;
    &lt;Coveredlines&gt;126&lt;/Coveredlines&gt;
    &lt;Coverablelines&gt;176&lt;/Coverablelines&gt;
    &lt;Totallines&gt;495&lt;/Totallines&gt;
  &lt;/Summary&gt;
  &lt;Assemblies&gt;
    &lt;Assembly name="BookFinder.Core.DLL" coverage="71.6"&gt;
      &lt;Class name="BookFinder.BookDepository" coverage="85.7" /&gt;
      &lt;Class name="BookFinder.BookListViewModel" coverage="50" /&gt;
      &lt;Class name="BookFinder.BoolProperty" coverage="50" /&gt;
      &lt;Class name="BookFinder.BoundPropertyStrategy" coverage="0" /&gt;
      &lt;Class name="BookFinder.ListProperty" coverage="75" /&gt;
      &lt;Class name="BookFinder.Property" coverage="100" /&gt;
      &lt;Class name="BookFinder.StringProperty" coverage="100" /&gt;
      &lt;Class name="BookFinder.ViewModelBase" coverage="81" /&gt;
    &lt;/Assembly&gt;
  &lt;/Assemblies&gt;
&lt;/CoverageReport&gt;</code></pre>

ReportGenerator also generates Html and LaTeX output, with a "summary" variant for each of the three output types.

The XML report would be most useful for inclusion in build result reports, but I found the HTML version easy to use to examine coverage results down to the method level.

<div class="images">
<a href="{static}/images/html_summary.png"><img title="html_summary" align="top" src="{static}/images/html_summary.png?w=270" alt="HTML Coverage Summary" width="270" height="300" /></a>&nbsp;<a href="{static}/images/html_detail.png"><img title="html_detail" align="top" src="{static}/images/html_detail.png?w=300" alt="HTML Coverage Detail" width="300" height="208" /></a>
</div>

I appreciate the coverage count by each of the lines - not as fancy as dotCover's "which tests cover this", but it could be a helpful clue when you're trying to decide what you need to do to improve your coverage.

<h2>Joining Coverage Runs</h2>
Perhaps your test are scattered in space or time and you want to get an overview of all the code that's covered by them. OpenCover doesn't really do anything special for you, but <strong>ReportGenerator has your back</strong>. Specify multiple input files on the command line, and the results will be aggregated and added to a comprehensive report:

<pre><code class="bat">ReportGenerator.exe output1.xml;output2.xml;output3.xml XmlReport Xml</code></pre>

<h2>DIY Auto-Deploy</h2>
There's no built-in auto-deploy for OpenCover. However, <b>I made my own auto-deployable package</b> like so:
<ol>
<li>install OpenCover</li>
<li>copy the `C:\Program Files (x86)\OpenCover` directory somewhere - call this your <i>package directory</i></li>
<li>uninstall OpenCover - you won't need it any more</li>
</ol>

Then I just made sure my coverage build step 
<ul>
<li>knew where the OpenCover package directory was (for the build system at the Day Job, I added it to our "subscribes")</li>
<li>used the `-register` flag mentioned above to register OpenCover before running the tests</li>
</ul>
That's it. No muss, no fuss. I did a similar (but easier, since there's no registration needed) trick with ReportGenerator, and all of a sudden I have a no-deploy system.

In less than an hour's work, I could upgrade a project so the build servers and all the developers could run a coverage target, with no action on their part, other than pulling the updated source tree and building. (Which is pretty much what the build server does all day long anyhow...)

<h2>DIY (for now) Coverage with Isoloator</h2>
Isoloator and OpenCover don't work together out of the box, but thanks to advice I got from <a href="http://www.hmemcpy.com/blog/">Igal Tabachnik</a>, Typemock employee, it was not hard to change this.

Isolator's supported coverage tools are partly configurable. There is a `typemockconfig.xml` under the Isolator install directory - typically `%ProgramFiles (x86)%\Typemock\Isoloator\6.0` (or `%ProgramFiles%`, I suppose). Mr. Tabachnik had me add
<pre><code class="xml">&lt;Profiler Name="OpenCover" Clsid="{1542C21D-80C3-45E6-A56C-A9C1E4BEB7B8}" DirectLaunch="false"&gt;
  &lt;EnvironmentList /&gt;
&lt;/Profiler&gt;</code></pre>
to the `ProfilerList` element, and everything meshed. His <a href="http://stackoverflow.com/questions/6698290/can-opencover-be-used-with-typemock-isolator">StackOverflow answer</a> provides full details and suggests that official support for OpenCover will be added to Isolator. 

<h2>IIS</h2>
I can't find any special IIS support. I'm not saying OpenCover can't be used to cover an application running in IIS, only that I didn't find any help for it. I may investigate this later.

<h2>Sequence Point coverage</h2>
OpenCover counts sequence points, not statements. Yay!

<h2>Conclusion</h2>
<strong>Pros:</strong>
<ul>
	<li>free</li>
        <li>open source</li>
        <li>active project</li>
	<li>XML/HTML/LaTeX reports (via ReportGenerator)</li>
	<li>report merging (via ReportGenerator)</li>
	<li>Isolator support is easy to add (and may be included in future Isolators)</li>
        <li>auto-deploy package is easy to make</li>
</ul>
<strong>Cons:</strong>
<ul>
	<li>no IDE integration</li>
	<li>no help with IIS profiling</li>
</ul>

I really like OpenCover. It's easy to use, relatively full-featured, and free. In a work environment, where there's a tonne of developers who want the in-IDE profiling experience, it may not be the best bet, but I'd use it for my personal .NET projects in a flash. 
