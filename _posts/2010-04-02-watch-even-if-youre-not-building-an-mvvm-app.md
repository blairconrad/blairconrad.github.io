---
layout: post
title: Watch, even if you're not building an MVVM App
comments: true
tags:
    - Coroutines
    - Development
    - Frameworks
    - MVVM
---
I'm about two weeks behind the wave, but this week I found the time to watch Rob Eisenberg's Mix 10 <a href="http://live.visitmix.com/MIX10/Sessions/EX15">Build your own MVVM Framework talk</a> (who says having the flu is all bad?).

It's well worth the hour and twenty minutes. If you haven't yet, grab a tea, fire up the video, and sit back. Seriously, I can't describe how much I enjoyed it. My impressions, in no particular order:

<ul>
<li>The warning about needing MVVM experience may be overstated - I've never worked with MVVM (or GUIs, really), and only had it described to me by The Guy in the Next Cubicle, and I felt like I followed along well enough. If you know what the <a href="http://en.wikipedia.org/wiki/Model_View_ViewModel">M, the V, and the VM</a> are, that may be all you need.</li>
<li>Having computers perform repetitive tasks for humans is cool - we should try more of that.</li>
<li>Even if you don't care about MVVM or GUI programming, the section about using .NET IEnumerables to implement <a href="http://en.wikipedia.org/wiki/Coroutine">Coroutines</a> (starting at around minute 48) is worth the price of admission - this looks like an extremely powerful technique to (among other things) remove some of the complexity of performing aynchronous calls. I'm going to keep an eye out for places that this could help me.</li>
<li>I really liked the message that Mr. Eisenberg kept hitting - the mini-framework is (just?) a way of crystalizing existing conventions and making them work for you. This is a very powerful point - presumably you have conventions that you and your coworkers follow, so why not try to get more out of them? Perhaps incongruously, this reminds me a little of the strongest argument in favour of using whitespace for flow control in Python - in many languages (say C), we use braces to tell the compiler where a block begins and ends, and whitespace to tell the humans - why not use one mechanism for both? The mini framework does a similar thing - when we name classes SearchView and SearchViewModel, we do it so the programmers know how the classes are related, so why require an additional statement or constructor parameter or whatever to link them up? If the framework understands the convention, it can do the work for you.</li>
<li>The live presentation certainly helped to understand things - it was much easier for me to follow this than to try to understand <a href="http://ayende.com/Blog/archive/2009/12/20/effectus-fatten-your-infrastructure.aspx">Effectus</a> from text and source, not to denigrate Ayende Rahien's efforts.</li>
<li>Another point I enjoyed - the framework is there to make 90% of the cases easier. If it turns out that something needs to be a little different because it's no performing well enough or something, you can do that too.</li>
<li>Somewhat tied to the previous point, but I can't remember if it was mentioned - having a framework implement your conventions not only saves you work, but it can strengthen your conventions. If the easiest thing to do to get something to work is to follow a set of conventions, then people will follow the conventions - in addition to everything else, the framework can serve as a reminder to experienced developers and a teaching aid to the tyros.</li>
</ul>
One thing I'd like to see sometime, and this would likely be better-suited to a short book or long paper, would be the evolution of an application from frameworkless to frameworkful. Mr. Eisenberg kept stressing how the framework grew out of existing conventions in the Game Library application. I'd really like to see a case study - at what point is a convention recognized and the decision made to formalize it? Did everything happen at once, at the beginning ("we'll call our classes BlahView and BlahViewModel, so we'll need a ViewModelToViewHookerUpper"), or as development progressed ("this is the fifth button I've created that's called Save and calls the Save method on the ViewModel - why can't the computer know that's what I want?")?

Anyhow, don't just listen to me. Watch for yourself.

Now I'm off to resist poring over the Day Job source code so see how we can fatten up our framework layer...
