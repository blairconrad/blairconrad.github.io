---
layout: post
title: Fixated on Fixie - the birth of a new unit test runner
tags: 
    - fixie
---

I enjoy reading about how software is made, and I like unit testing frameworks. So, when I heard about <a href="http://www.headspring.com/author/patrick/">Patrick Plioi</a>'s new project <a href="http://plioi.github.io/fixie/">Fixie</a>, I rushed to check it out.

<p>In this case, "check it out" doesn't mean "clone the repo and dig around the source code". Nor does it mean "install the NuGet package and build something". Although I may do those things in the future.</p>

<p>Nope. It means I read Mr. Plioi's articles about Fixie and its development. And I am having a great time. Moreso than hearing about Fixie's features (or more often lack of features), I'm enjoying seeing Mr. Plioi's approach to setting up a new project, including:</p>
<ul>
<li>prototyping the scariest integration points first</li>
<li>the importance of starting out with a one-click build, for himself and for potential future contributors</li>
<li>streamlining, automating, or eliminating as much ceremony as possible</li>
<li>bootstrapping, and more!</li>
</ul>

<p>The articles are well-written and articulate, and mildly funny. They're trending a little more into the implementation of Fixie itself, rather than guiding philosophies, but I still find them interesting. And it's worth noting that all the while I was enjoying the articles, I was thinking in the back of my head "this is a great exercise, and very instructive, but I've no interest in actually <i>using</i> Fixie&mdash;I'm content with <a />NUnit</a>". Until I read <a href="http://www.headspring.com/dry-test-inheritance/">DRY Test Inheritance</a>. I really liked the low-ceremony way conventions are used to locate test setups and teardowns. It hooked me. <i>Even though I am usually not a fan of test class inheritance and the scheme described in this article has more weight than the <a href="https://github.com/plioi/fixie#default-convention">Default Convention</a>.</i></p>

<p>Of course, we'll probably never switch at the Day Job, at least not until the <a href="http://www.jetbrains.com/resharper/features/unit_testing.html">ReSharper test runner</a> supports Fixie, but it might be fun to use for a small home project.</p>