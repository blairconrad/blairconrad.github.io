---
layout: post
title: Hasty Impressions&#58; NCover
comments: true
tags:
    - .NET
    - coverage
    - HastyImpressions
    - IIS
    - Isolator
    - NCover
    - Testing
    - TypeMock
---
{% include series-net-coverage-tool.html %} 

I tried NCover 3.4.18.6937. 
<h2>The Cost</h2>
NCover Complete is $479 plus $179 for a 1-year subscription (which gives free version updates). I thought this was <b>a little steep</b>. NCover Classic is $199/$99. I looked at NCover Complete, because that's the kind of trial version they give out. Also, the feature set for Classic was too similar to that offered by other tools that cost less. Check out the <a href="http://www.ncover.com/pages/feature_comparison">feature comparison</a>, if you like.
<h2>Support</h2>
I haven't had enough problems to really stress the support network, but I will say this - the NCover chaps are really keen on keeping in touch with people who have trial copies of the program. I've received 3 separate e-mails from my assigned NCover rep in the 2 weeks since I first installed my trial copy. I replied to one of these, asking for a clarification on the VS integration (see below), and got a speedy response. 
It's nice to see such a <b>high level of customer support</b>, but I do feel just a little bit smothered&hellip;
<!--more-->

<h2>VS integration</h2>
The best advice from the NCover folks is to <a href="http://docs.ncover.com/how-to/running-ncover-from-visual-studio/">create an external tool to launch NCover</a>. That's an okay solution if you want to run all the unit tests in a project and profile them, but it <b>lacks flexibility</b>. Then to actually look at the report, you have to launch the NCover Explorer and load the report.

There's additional advice at the end of the <i>Running NCover from Visual Studio</i> video - if you want a more integrated Visual Studio experience, you should obtain <a href="http://testdriven.net/">TestDriven.Net</a>. That probably works well enough, but I'm not wild about paying an additional $189 per head (roughly) for a test runner that (in my opinion, and excepting the NCover integration of course) is a less robust solution than the one that <a href="http://www.jetbrains.com/resharper/features/unit_testing.html">comes bundled with ReSharper</a>.

Oh. There's one more feature that I found - once you are examining a coverage report, you can <code>Edit in VS.NET</code>, which opens the appropriate file in Visual Studio. This is somewhat convenient, but doesn't warp you to the correct line, which is a bit of a letdown.

<h2>Command Line Execution</h2>
The command line offers many and varied options for configuring the coverage run. Here's a sample invocation:

<pre><code class="bat">NCover.Console.exe //exclude-assemblies BookFinder.Tests //xml ..\..\coverage.nccover nunit-console.exe bin\debug\BookFinder.Tests.dll</code></pre>

Upon execution, NCover tells me this:


Adding the `/noshadow` argument to the NUnit command line to ensure NCover can gather coverage data.
To prevent this behavior, use the `//literal` argument.

I really like that it defaults to passing the recommended <code>/noshadow</code> to NUnit. The <code>//</code> switches are also a good touch - it makes providing arguments to the executable being covered a lot easier. These features make the command line invocation <b>the best I've seen</b> among coverage tools.

<h2>GUI Runner</h2>
<div class="images">
<a href="{{ site.image_dir }}/runncover.png"><img src="{{ site.image_dir }}/runncover.png" width="300" height="397"  alt="NCover options" title="RunNCover"/></a><a href="{{ site.image_dir }}/nocoverexplorer.png"><img src="{{ site.image_dir }}/ncoverexplorer.png" height="397" width="515" alt="" title="NCoverExplorer"  /></a>
</div>

The GUI runner looks just like a GUI wrapper on top of the command line options - they appear to support the same level of configuration. After the tests have been run, the NCoverExplorer allows one to browse the results and to save a report as XML or HTML.

<h2>XML Report</h2>
Reports are generated either from the GUI runner or by using the NCover.Reporting executable, which has a plethora of options for choosing XML or HTML reports of various flavours.
XML reports contain all the information you might want to summarize for inclusion in build output, but they're <b>hard to understand</b>. Witness:

<pre><code class="xml">&lt;stats acp="95" afp="80" abp="95" acc="20" ccavg="1.5" ccmax="5" ex="0" ei="1" ubp="12" ul="40" um="10" usp="39" vbp="63" vl="89" vsp="105" mvc="18" vc="2" vm="22" svc="120"&gt;</code></pre>

If you stare at this long enough (and correlate with a matching HTML report), you figure out that this means that there are
<ul>
<li>39 <b>u</b>nvisited <b>s</b>equence <b>p</b>oints, and</li>
<li>105 <b>v</b>isited <b>s</b>equence <b>p</b>oints</li>
</ul>
along with various other stats, so using attribute extraction and Math, we could see that 105/144 or 72.9% of the sequence points are covered.

It's odd that there are many more reports available for HTML than XML. Notably absent from the XML offering: "Summary". What is it about summaries that make them unsuitable for rendering as XML when HTML is fine?
<h2>Reports of Auto-Deploy</h2>
My Support Guy explained that you can xcopy deploy NCover using the <code>//reg</code> flag, but I <b>did not find any documentation</b> on how to do this. Support Guy claims there is an "honour system" kind of licensing model that supports this, but the trial copy I had did not work this way. I eventually abandoned this line of investigation.

<h2>Mature Isolator Support</h2>
From Visual Studio, under the Typemock menu, configure Typemock Isolator to Link with NCover&nsbsp;3.0.
When using the <code>TypeMockStart</code> MSBuild task, use
<pre><code class="xml">&lt;TypeMockStart Link="NCover3.0" ProfilerLaunchedFirst="true"&gt;</code></pre>
and it <b>just works</b>, assuming you have TypeMock Isolator installed or <a href="/2010/06/06/auto-deploying-typemock-isolator-without-trashing-the-installation/">set to auto-deploy</a>.
<h2>IIS</h2>
IIS coverage is available, simply by selecting it from the <b>GUI runner options or from the command line</b> using the <code>//iis</code> switch. Other Windows Services can be covered in the same manner. Note though, that these features are only available in the Complete flavour of NCover 3.0.
<h2>Sequence Point coverage</h2>
<b>Supported</b>, as well as branch point coverage and other metrics, including <a href="http://en.wikipedia.org/wiki/Cyclomatic_complexity">cyclomatic complexity</a>. Nice options to have, although probably a little advanced for my team's current needs and experience.
<h2>Conclusion</h2>
<strong>Pros:</strong>
<ul>
<li>sequence point and branch coverage</li>
<li>large feature set, including trends, cyclomatic complexity analysis, and much much more</li>
<li>commercial product with strong support</li>
<li>report merging</li>
<li>easy IIS profiling</li>
<li>supports Isolator</li>
</ul>
<strong>Cons:</strong>
<ul>
<li>costly</li>
<li>weak IDE integration</li>
<li>inconsistent (comparing XML to HTML) report offerings</li>
<li>confusing auto-deploy</li>
</ul>
I expected to be blown away by NCover&mdash;from all reports, it's the Cadillac of .NET coverage tools. After demoing it, I figured I'd end up desperately trying to make a case to the Money Guy to shell out hundreds of dollars per developer (and build server), but this did not happen.
While NCover definitely has lots of features, it's lacking some pretty important ones as well, notably IDE integration. Other features just weren't as I expected - the cornucopia of report types is impressive, but overkill for a team just starting out, and many of the report types aren't available in XML and/or are very minor variations on other report types.
Ultimately, I don't see what NCover offers to justify its price tag, especially across a large team. If ever I felt a need to have one of the specialized report, I'd consider obtaining a single license for tactical use, but I can't imagine any more than that.
