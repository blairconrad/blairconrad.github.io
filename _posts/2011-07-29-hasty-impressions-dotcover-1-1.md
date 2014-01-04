---
layout: post
title: Hasty Impressions&#58; dotCover 1.1
tags:
    - .NET
    - coverage
    - dotCover
    - HastyImpressions
    - IIS
    - Isolator
    - MightyMoose
    - Testing
    - TypeMock
---
{% include series-net-coverage-tool.html %} 

Today I'm looking at the first candidate: <a href="http://www.jetbrains.com/dotcover/">JetBrains dotCover</a>.

I tried dotCover 1.1, integrated with ReSharper 5.1 running in VS2008.
<h2>The Cost</h2>
A lifetime license, with 1 year of free upgrades is <s>$199</s> $149 - a special introductory price.

This isn't usurious, but considering that ReSharper C# edition, a tool that changes the way I work every single day, is $249, it's enough.
<h2>VS integration</h2>

<a href="{{ site.image_dir }}/cover_with_dotcover2.png"><img style="margin-right:1em;" title="cover with dotCover" src="{{ site.image_dir }}/cover_with_dotcover2.png" alt="cover with dotCover" width="174" height="170" align="left" /></a>

This is where I expected dotCover to shine, and it didn't disappoint - the <strong>integration with Visual Studio (and with ReSharper) was excellent</strong>. The first thing I noticed was an extra "Cover with dotCover" item in the ReSharper test menu (triggered from the yellow and green ball things). I clicked it, and it ran my tests, bringing up the familiar Unit Test results window.

Once the tests ran, there was pause while dotCover calculated the coverage info, and then the bottom pane filled in with coverage results: green/red bars by every method in the covered assemblies. Clicking on the methods warps to the source code, which is also highlighted - covered statements have a green background, and uncovered statements have red. In fact, every source file opened in the IDE has the highlighting.

<a href="{{ site.image_dir }}/doccover_bookfinder.png"><img title="dotCover BookFinder tests" src="{{ site.image_dir }}/doccover_bookfinder.png?w=300" alt="dotCover BookFinder tests" width="300" height="233" align="top" /></a><a href="{{ site.image_dir }}/dotcover_covered.png"><img title="dotCover_covered" src="{{ site.image_dir }}/dotcover_covered.png?w=300" alt="" width="300" height="187" align="top" /></a>
<h3>Finding tests that cover code</h3>
The most interesting feature that dotCover has is the ability to identify which tests covered which lines of code. I'm not entirely sold on this, thinking it more of a gimmick than anything else. When I first heard about it, I thought "I don't care which test covered which line, so long as the lines are covered. I'm here to see what <em>isn't</em> covered.". Yes, I think in italics sometimes.

<a href="{{ site.image_dir }}/dotcover_show_covering_tests.png"><img style="margin-left:1em;margin-bottom:1em;" title="dotCover_show_covering_tests" src="{{ site.image_dir }}/dotcover_show_covering_tests.png" alt="" width="278" height="140" align="right" /></a>Still, I gave it a go. Right-clicking on a line of code (once coverage has been run) brought up a tiny menu full of covered lines of code. I don't know why, but it made me happy. I suppose one could use this from time to time to make sure a new test case is exercising what it's supposed to, but normally I can tell that by how a new test fails, or by what I've typed just before the test starts working. Worst case, I could always debug through a single test - something made very easy by the ReSharper test runner.

<a href="{{ site.image_dir }}/dotcover_covering_tests.png"><img class="alignright size-medium wp-image-1080" title="dotCover_covering_tests" src="{{ site.image_dir }}/dotcover_covering_tests.png" /></a>
There was one aspect of this feature that I could imagine someone using - the ability to <strong>run the tests</strong> that cover a line of code. All that's needed is to hit the "play" button on the "Show Covering Tests" popup. If the full suite of tests takes a very long time to run, this could be useful. Still, it doesn't do much for me personally - if my tests took that long to run, I'd try speed them up. If nothing else, I would probably just run the test fixture designed to test the class or method in question, instead of my entire bolus of tests.

So, running tests that cover some code is a cool feature, but it's <strong>not that useful</strong>. I'd rather see something like the automatic test runs and really cool "what's covered" information provided by <a href="http://continuoustests.com/">Mighty-Moose</a>.
<h2>Command Line Execution</h2>
Covering an application from the command line is <b>pretty straightforward</b>. I used this command to see what code my BookFinder unit tests exercised:
{% highlight bat %}
dotcover cover /TargetExecutable=nunit-console.exe /TargetArguments=.\BookFinder.Tests.dll /Output=dotCoverOutput /Filters=+:BookFinder.Core
{% endhighlight %}
BookFinder.Core is the only assembly I was interested in - it holds the business logic. "cover" takes multiple include and exclude filters, even using wildcards for assemblies, classes, and methods.

One quite cool feature is to use the <b>help subcommand to generate an XML configuration file</b>, which can be used to specify the parameters for the <code>cover</code> command:
{% highlight bat %}
dotCover help cover coverSettings.xml
{% endhighlight %}
will create a <code>coverSettings.xml</code> file that can be edited to specify the executable, arguments, and filters. Then use it like so:
{% highlight bat %}
dotCover cover coverSettings.xml
{% endhighlight %} without having to specify the same batch of parameters all the time.

<h2>Joining Coverage Runs</h2>
Multiple coverage snapshots - perhaps from running tests on different assemblies, or just from performing different test runs on the same application - <b>can be merged together</b> into a comprehensive snapshot:
{% highlight bat %}
dotCover merge /Source snapshot1;snapshot2 /Output mergedsnapshot
{% endhighlight %}
Just include all the snapshots, separated by semicolons. 
<h2>XML Report</h2>
After generating snapshots and optionally merging them, they can be  <b>turned into an XML report using the report command</b>:

{% highlight bat %}dotcover report /Source=.\dotCoverOutput /Output=coverageReport.xml{% endhighlight %}

There are options to generate <b>HTML</b> and <b>JSON</b> as well.

Note that if there's only one snapshot, the "merge" step is not needed. In fact, there's even a separate <code>analyse</code> command that will cover and generate a report in one go.

<h2>No Auto-Deploy</h2>
There's no auto-deploy for dotCover - <strong>it needs to be installed</strong>. And since it's a plugin, <strong>Visual Studio is a requirement</strong>. This is a small inconvenience for developers and our build servers. Having to put VS on all our test machines is a bit of a bigger deal - definitely a strike against dotCover.

<h2>TypeMock Isolator support in the future</h2>
The dotCover 1.1 doesn't integrate with Isolator 6. Apparently dotCover's hooks are a little different than many other profiles (nCover, PartCover, …). I've been talking to representatives from both TypeMock and JetBrains, though, and they tell me that the problem is solved, and an upcoming release of Isolator will integrate with dotCover. <a href="http://forums.typemock.com/viewtopic.php?p=8528">Even better, a pre-release version that supports the latest dotCover EAP is available now</a>.
<h2>IIS</h2>
dotCover <b>covers IIS, but only by using the plugin</b> - this means that the web server has to have Visual Studio and dotCover installed, and it's a manual step to invoke the coverage. In the JetBrains developer community there's a <a href="http://devnet.jetbrains.net/thread/30319">discussion about command-line IIS support</a>, but no word from JetBrains staff on when this might come.

<h2>Statement-level coverage</h2>
As <a href="http://vcsjones.com/2011/01/03/dotcover-inaccurate-or-misunderstood/">Kevin Jones notes</a>, dotCover reports coverage of statements coverage, not sequence points. This means that a line like this:
{% highlight bat %}
return value &gt; 10
      ? Colors.Red
      : Colors.White;
{% endhighlight %} 
Will report as completely covered, even if it's executed only once - in order to ensure an accurate coverage report for this idea, the <code>?:</code> would have to be replaced by an if-else block.
This isn't necessarily a major strike against the tool, but it's worth knowing, as it will skew the results somewhat.

<h2>Conclusion</h2>
<b>Pros:</b>
<ul>
<li>awesome IDE integration</li>
<li>XML/HTML/JSON reports</li>
<li>report merging</li>
<li>IIS profiling</li>
</ul>
<b>Cons:</b>
<ul>
<li>moderate price</li>
<li>no auto-deploy</li>
<li>no Isolator support&mdash;yet</li>
</ul>

Overall, I like the tool. I'm a little disappointed by the lack of auto-deploy and the inability to run IIS coverage from the command line, but those problems can be worked around. I was very impressed with the in-IDE support as well as the automatically generated configuration files using the "help" subcommand.
Ordinarily, the I'd say the current lack of Isolator support is a deal-breaker, but I recently demoed the product to some colleagues, and <b>they went bonkers for the IDE integration</b>. I guess I'll be writing JetBrains and TypeMock looking for the betas. 
