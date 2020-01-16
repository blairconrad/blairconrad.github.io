---
layout: post
title: Limit FakeItEasy extension scanning with a bootstrapper 
comments: true
tags: FakeItEasy
---

**As of version [1.18.0][release], a client-supplied bootstrapper can be used to
determine which external assembly files are scanned during startup.**

Last time, I talked about how [FakeItEasy extension scanning had
improved in version 1.13.0][betterscan]. While this change has dramatically
improved startup times in many situations, we recently [received a
comment from one of our valued clients][complaint] (and subsequently a [pull
request with a proposed solution][pull]), detailing a situation where startup was
taking about 13 seconds, mostly due to a huge number of assemblies in
the working directory. Disabling [shadow copy][shadows] creation by the test
runner alleviated the pain, but the incident prompted a re-examination
of the issue.

While disabling shadow copies should resolve most slow startup
problems caused by excessive working directory assemblies, and it may
[improve performance in other ways][shadowstart], recommending this to clients
has always felt like a bit of a dodge to me, essentially pushing the
problem off to someone else. There was also the lingering fear that
someone would come back with a reason why the shadow copies were
necessary.

We wanted to provide FakeItEasy's clients with a little more control
over the process of scanning for assemblies. So, we've implemented the
originally-proposed bootstrapper solution. 

## Using a custom bootstrapper

By default, after scanning all FakeItEasy-referencing assemblies
currently loaded in the AppDomain, FakeItEasy&nbsp;1.18.0 will examine all DLLs in
the working directory. This behaviour can be changed by including in
the AppDomain a class that implements `FakeItEasy.IBootstrapper`. As I
write, this is the only behaviour that the bootstrapper controls:

<pre><code class="csharp">/// &lt;summary&gt;
/// Provides a list of assembly file names to scan for extension points, such as
/// &lt;see cref="IDummyDefinition"/&gt;s, &lt;see cref="IArgumentValueFormatter"/&gt;s, and 
/// &lt;see cref="IFakeConfigurator"/&gt;s.
/// &lt;/summary&gt;
/// &lt;returns&gt;
/// A list of absolute paths pointing to assemblies to scan for extension points.
/// &lt;/returns&gt;
IEnumerable&lt;string&gt; GetAssemblyFileNamesToScanForExtensions();&lt;/code&gt;&lt;/pre&gt;

The best way to implement the interface is to **extend
`FakeItEasy.DefaultBootstrapper`**. This class defines the default
FakeItEasy setup behaviour, so using it as a base allows
clients to customize only those aspects of the initialization that
matter to them.

While any list of assembly files can be provided by
`GetAssemblyFileNamesToScanForExtensions`, I expect that most
extensions that are defined will already be loaded in the current
AppDomain, so the most common customization will be to disable
external assembly scanning, like so:

&lt;pre&gt;&lt;code class="csharp"&gt;public class NoExternalScanningBootstrapper : FakeItEasy.DefaultBootstrapper
{
    public override IEnumerable&lt;string&gt; GetAssemblyFilenamesToScanForExtensions()
    {
        return Enumerable.Empty&lt;string&gt;();
    }
}</code></pre>

Of course, if there _were_ extensions defined in an external assembly
file or two, the `GetAssemblyFilenamesToScanForExtensions`
implementation could return the paths to just those assemblies.

[betterscan]: {% post_url 2013-07-08-better-formatter-auto-discovery-in-fakeiteasy-1.13.0 %}
[complaint]: https://github.com/FakeItEasy/FakeItEasy/issues/130#issuecomment-33688273
[shadows]: http://msdn.microsoft.com/en-us/library/ms404279(v=vs.110).aspx
[shadowstart]: http://msdn.microsoft.com/en-us/library/ms404279(v=vs.110).aspx#StartupPerformance
[pull]: https://github.com/FakeItEasy/FakeItEasy/pull/251
[release]: https://github.com/FakeItEasy/FakeItEasy/releases/tag/1.18.0
