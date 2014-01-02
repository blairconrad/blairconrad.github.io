---
layout: post
title: Best all-around .NET coverage tool - OpenCover
tags: 
    - .NET
    - coverage
    - OpenCover
---

{% include series-net-coverage-tool.html %}

This is the gala awards show, where my chosen coverage tool is announced. 

If you've come this far, you've probably already read the title, and it won't surprise you to learn that I've chosen <a href="https://github.com/sawilde/opencover">OpenCover</a>. It offered the best fit for my requirements - the only areas where I found it lacking were in the "nice to haves". <!--more-->Witness:
<ul>
   <li>OpenCover is pretty easy to <strong>run from the command line</strong> - second only to NCover.</li>
   <li>It can (with the help of ReportGenerator) generate <strong>coverage reports in XML and HTML</strong>.</li>
   <li>OpenCover has an integrated <strong>auto-deploy</strong>, so it can be bundled with the source tree and new developers or build servers just work - dotCover has no such option, and I was not able to use NCover this way.</li>
   <li>I've been able to <strong>link with TypeMock Isolator</strong> with little trouble, and the new Isolator may obviate the need for my small workaround.</li>
   <li><strong>It's free</strong>. Aside from the obvious benefit, it's nice to not have to count licenses when adding developers and/or build server nodes.</li>
   <li>There's <b>no GUI integration</b>, but this was a nice to have. If some developer is absolutely dying to have this, my boss's boss has indicated that money could be available for individual licenses of something like dotCover.</li>
   <li>There's <b>no support for integrating with IIS</b>. We don't need this right now, so that's okay. Again, if we one or two developers find a need, we have the option of buying a license of some other tool. Even better, support <a href="https://github.com/sawilde/opencover/issues/36">may be coming soon</a>.</li>
</ul>

After considering OpenCover's strengths in the areas I absolutely
needed, and its weaknesses, which all appear to be in areas that I
care a little less about, I recommended it the boss's boss, who agreed
with the assessment and was happy to keep a little money in his pocket
for now.

So, I grabbed 2.0.802, incorporated it into one product's build, and out popped coverage numbers. Very exciting. I did notice a few things, though:
<ol>
<li>Branch coverage has been added since I last evaluated the product!</li>
<li>One fairly complicated integration-style testfixture is not runnable under OpenCover - the class tested creates a background thread and starting the thread results in a <code>System.AccessViolationException</code>. I was unable to determine the cause of this, and have temporarily removed the test from coverage, instead executing it with NUnit directly. I'm going to continue investigating this problem.</li>
<li>Since I'm XCopy deploying, I was bitten by <a href="https://github.com/sawilde/opencover/issues/52">the dependency on the Microsoft Visual C++ 2010 Redistributable Package</a> - I ended up including the DLLs in my imported bundle, and all was well, but I worry a little about the stability of this solution.</li>
<li>The time taken to execute our tests (there are over 5000, and many hit a database) increased from about 7 minutes to about 8. This is an acceptable degradation, since the test run isn't the bottleneck in our build process.</li>
<li>The number of "Cannot instrument  as no PDB could be loaded" messages is daunting. I'm hoping that things will be improved once I get a build that contains a fix for <a href="https://github.com/sawilde/opencover/issues/40">issue 40</a>.</li>
</ol>