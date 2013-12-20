---
layout: post
title: Better formatter auto-discovery in FakeItEasy 1.13.0
tags: .NET FakeItEasy Nancy
---

A few weeks ago, I wrote about
[the
problems that FakeItEasy's assembly scanning was causing]({% post_url 2013-06-17-fakeiteasys-argument-formatter-auto-discovery-boon-and-inconvenience %}) while it
was looking for user-defined extensions. To recap, FakeItEasy was
scanning all assemblies in the AppDomain and the working directory,
looking for types that implemented `IArgumentValueFormatter`,
`IDummyDefinition`, or `IFakeConfigurator`. This process was quite
slow. Worse, it raised LoaderLock exceptions when debugging, and
Runtime errors anytime I ran my tests using the ReSharper test runner.

At that time, I'd opened <a
href="https://github.com/FakeItEasy/FakeItEasy/issues/130">issue
130</a>, intended to allow configuration of the scanning
procedure. I'm happy to say that the issue has been closed "no
fix". Instead, I've contributed the fix for <a
href="https://github.com/FakeItEasy/FakeItEasy/issues/133">Issue 133
&mdash; Improved performance of assembly scanning</a>. It doesn't
introduce any configuration options, but streamlines the scanning
process.

The **original behaviour** was:

1. find all the DLLs in the application directory
1. load all the found DLLs
1. find the distinct assemblies among those loaded from the directory and those already in the AppDomain
1. scan each assembly and add all the types to a list

The **new behaviour**, heavily inspired by <a href="http://nancyfx.org/">Nancy</a>'s bootstrapper-finding code, is:

1. find all the DLLs in the application directory
1. discard DLLs that are already part of the AppDomain - We don't even have to crack these files open again, since we already know everything about them. Note that this check **examines the absolute paths to the DLL and the loaded assembly, and will be fooled by shadow copying**. So, if your test runner makes shadow copies, this time won't be saved. I turned off shadow copying with no ill effects (and a tremendous speedup), but your mileage may vary.
1. load each remaining DLL _for reflection only_ - This may be faster, and it may not, but it has another big advantage - it **doesn't cause any of the code in the assembly to execute**. (It was the execution of the assembly code that caused my LoaderLock and Runtime errors.)
1. for each assembly that references FakeItEasy, fully load it - If we don't do this, we can't scan for all the types in the assembly because 

    > When using the ReflectionOnly APIs, dependent assemblies must be pre-loaded or loaded on demand through the ReflectionOnlyAssemblyResolve event

    according to the <a href="https://github.com/FakeItEasy/FakeItEasy/issues/133#issuecomment-19728061">error I got when I tried it</a>. Note that excluding assemblies that don't reference FakeItEasy means **we only examine assemblies that could possibly define formatting/dummy/configuration extensions**, cutting down on the scanning time.

1. scan each of the following, remembering all contained types:

    * the assemblies we just loaded from files,
    * the AppDomain assemblies that reference FakeItEasy, and
    * FakeItEasy - We need to include FakeItEasy explicitly because it
      defines its own formatter extensions, and since we're otherwise
      only looking at assemblies that reference FakeItEasy, we'd miss
      it.

This new scanning behaviour has been released in the <a
href="https://www.nuget.org/packages/FakeItEasy/1.13.0">FakeItEasy
1.13.0 build</a>, and has been a boon to me already. I'm enjoying the
faster test runs (0.534 seconds for my first test, versus 1.822 (or
more)) and the improved stability of the test runner. NuGet it now.