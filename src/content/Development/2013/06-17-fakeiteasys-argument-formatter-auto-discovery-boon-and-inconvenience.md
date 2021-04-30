---
layout: post
title: FakeItEasy's argument formatter auto-discovery - boon and inconvenience
comments: true
tags: .NET, FakeItEasy
---
Hi again. At the Day Job, we've recently dropped [Typemock Isolator](http://www.typemock.com/isolator-product-page) and [NMock2](http://sourceforge.net/apps/mediawiki/nmock2) as the mocking frameworks of choice in the products that I work on. We've jumped on the [FakeItEasy](http://fakeiteasy.github.io) bandwagon. So far, we're enjoying the change. FakeItEasy is powerful enough and the concepts and syntax fit the mind pretty well. Today I'm going to focus on one feature that I've really enjoyed but that has been an occasional thorn in the side.

This is a feature that [Patrik Hägne has blogged about before](http://ondevelopment.blogspot.ca/2010/09/extending-exception-messages-in.html), but that I think is still not well known. I found it accidentally, and have benefited from it. You can provide custom argument renderers to **improve the messages** you get when FakeItEasy detects an error due to missing or mismatched calls. Check out Mr. Hägne's post for the full details, but if I may be so bold as to rip off some of his examples, here's the gist (original meaning, not fancy github one).

<!--more-->

Define a class that extends `ArgumentValueFormatter<Person>` (where Person is a class in your project), override `GetStringValue` with something that renders a Person, and FakeItEasy errors that need to talk about a Person change from this
<pre>Assertion failed for the following call:
    'FakeItEasy.Examples.IPersonRepository.Save()'
  Expected to find it exactly never but found it #1 times among the calls:
    1.  'FakeItEasy.Examples.IPersonRepository.Save(
            personToSave: FakeItEasy.Examples.Person)'</pre>

to
<pre>Assertion failed for the following call:
    'FakeItEasy.Examples.IPersonRepository.Save()'
  Expected to find it exactly never but found it #1 times among the calls:
    1.  'FakeItEasy.Examples.IPersonRepository.Save(
            personToSave: <b>Person named Patrik Hägne,
                          date of birth 1977-04-05 (12227,874689919 days old).)</b>'</pre>

It's very easy to use, and quite helpful. However, lately I've had a few difficulties with some test projects and have tracked it back to an aspect of this feature. Specifically, for certain very large projects

* My test fixtures are <b>taking a long time to start up</b> - several extra seconds while waiting for the first test to run. Specifically, the delay was happening in my first `A.Fake` call.
* During this delay, several "<b>LoaderLock was detected</b>" popups appear, which have no obvious ill effect, but are very annoying, and
* Finally, after a recent upgrade of dependent libraries, when I run the tests using the [Resharper test runner](http://www.jetbrains.com/resharper/features/unit_testing.html), I see a "Microsoft Visual C++ Runtime Library **Runtime Error!**" in JetBrains.ReSharper.TestRunner.CLR4.exe. It claims that I'm trying to "use MSIL code from this assembly during native code initialzation". The tests continue to run, but the TestRunner process never exits, and needs to be killed before test can be run again.

The reasons all these things are happening during the first FakeItEasy call is due to the way that FakeItEasy finds the custom `ArgumentValueFormatter` implementations. It <b>scans all available assemblies</b>, looking for any implementations. In this case, "all available assemblies" means every assembly in the `AppDomain` as well as all `*.dll` files in the current directory. This actually makes the feature a little more powerful than Mr. Hägne indicated&mdash;you can define your extensions in other assemblies than the test project's. In fact, this is how FakeItEasy finds its own built-in `ArgumentValueFormatter`s (one for `null`, one for `System.String`, and one for any `System.Object` that doesn't have its own extensions). FakeItEasy is in the AppDomain, so its extensions are located by the scan. One benefit of doing such a wide scan is that <b>it's possible to define the formatter extension classes in a shared library</b> that can be used across test projects.

It's the scanning that's causing my pain. First, some of the solutions at the Day Job are quite large, with dozens of assemblies in the test project's AppDomain and build directory. Even if everything went well, it would take seconds to load and scan all those assemblies.  Second, some of the DLLs in the directory aren't under our control. Some aren't managed. Some don't play well with others. It's these ones that are causing the other problems I mentioned above. <b>Loading these assemblies causes them to be accessed in ways that they were never planned to be</b>, which causes the LoaderLocks and Runtime Error.

What now? We're investigating the assemblies we're using to see if we can't access them in a better way, but that's probably going to be a slow operation, and one that may not bear fruit. In the meantime, I've forked FakeItEasy and am using the custom build in the one project that it was causing the most pain. <b>The custom version only loads extensions from the FakeItEasy assembly</b>. It's kind of a terrible hack, and means that we can't define custom extensions, but we hadn't for that project anyhow, so it's not yet causing pain. On the brighter side, there are no more errors or popups, and the tests start much more quickly.

Longer term, I've created <a href="https://github.com/FakeItEasy/FakeItEasy/issues/130">FakeItEasy issue 130 to make the extension location a little more flexible</a>. Once accepted and implemented, it will give the user control over how extension classes are located during FakeItEasy startup. (Then I can resume using the vanilla FakeItEasy at the Day Job.) If you're curious, pop on over and take a look.

