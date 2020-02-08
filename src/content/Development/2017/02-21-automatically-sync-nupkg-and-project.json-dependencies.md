---
layout: post
title: Automatically Sync nupkg and project.json Dependencies 
comments: true
tags: .NET
---

Recently while working on an open source .NET project,
I forgot to update the `.nuspec` after changing a package
dependency in my `project.json`. Of course the resulting nupkg
contained the wrong dependency. Fortunately, the package
wasn't published in that state, but I didn't want to risk such a thing
happening again.

I want the project to be buildable in Visual Studio immediately
after cloning, but there's no such constraint on producing the NuGet
package, so this means the `project.json` has to be the source
of truth.

I opted to have the project's
[simple-targets-csx](https://github.com/adamralph/simple-targets-csx)
build script scrape the `project.json` for the version of the
dependent package and supply the matching version as part of the
[nuget pack](https://docs.microsoft.com/en-us/nuget/tools/nuget-exe-cli-reference#pack)
`properties` option.

My initial implementation used a regular expression to extract the
version, but my colleague
[Thomas Levesque](http://www.thomaslevesque.com/) suggested parsing
the JSON to find the proper value.

I liked the idea, but pulling in something like
[Json.NET](http://www.newtonsoft.com/json) seemd heavy. A little
Googling later, I found Brandur Leach's
[Using the Little-known Built-in .NET JSON Parser](https://mutelight.org/using-the-little-known-built-in-net-json-parser)
that described the built-in
[JsonReaderWriterFactory](https://msdn.microsoft.com/en-us/library/system.runtime.serialization.json.jsonreaderwriterfactory(v=vs.110).aspx).
This seemed like just the ticket. A few minutes later, I was up and
running with these sections of the build script

<pre><code class="csharp">targets.Add(
    "pack",
    DependsOn("build", "outputDirectory"),
    () =>
    {
        var fakeItEasyVersion = GetDependencyVersion("FakeItEasy");
        Cmd(nuget, $"pack {nuspec} -Version {version} -Properties FakeItEasyVersion={fakeItEasyVersion} -OutputDirectory {outputDirectory} -NoPackageAnalysis");
    });

…

public string GetDependencyVersion(string packageName)
{
    byte[] buffer = File.ReadAllBytes(projectJsonPath);
    XmlReader reader = JsonReaderWriterFactory.CreateJsonReader(buffer, new XmlDictionaryReaderQuotas());

    XElement root = XElement.Load(reader);
    return root.Element("dependencies").Element(packageName).Value;
}</code></pre>

which find the "3.0.0-rc001-build000097" from the project.json:

<pre><code class="json">{
  "dependencies": {
    "FakeItEasy": "3.0.0-rc001-build000097",
    "StyleCop.Analyzers": "1.1.0-beta001"
  },
  …</code></pre>

and combine it with this portion of the `.nuspec`:

<pre><code class="xml">&lt;dependencies&gt;
  &lt;dependency id="FakeItEasy" version="[$FakeItEasyVersion$,4)" /&gt;
&lt;/dependencies&gt;</code></pre>

Of course, a property could be added for each dependency. Do this, and
you can rest easy, knowing you'll never get a dependency mismatch
again.
