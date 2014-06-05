---
layout: post
title: "Automatically Printing Rake (or other Ruby) Variables" 
comments: true
tags: 
      - rake
      - ruby
      - local_variables
---

The [FakeItEasy][fakeiteasy] rakefile contains a `vars` target
(brainchild of [Adam Ralph][adamralph]) that can be used to print out
the local variables defined in the script. Mostly these are static
variables, such as the path to the [NUnit][nunit] command, but some,
such as the upcoming FakeItEasy version, are computed. Logging these
computed variables can help debug misbehaving builds.

If ever something goes wrong, we can check the [TeamCity][teamcity]
build log and see something like this:

<pre>
assembly_info:     Source/CommonAssemblyInfo.cs
mspec_command:     Source/packages/Machine.Specifications.0.8.0/tools/mspec-clr4.exe
nuget_command:     Source/packages/NuGet.CommandLine.2.8.0/tools/NuGet.exe
nunit_command:     Source/packages/NUnit.Runners.2.6.3/tools/nunit-console.exe
nuspec:            Source/FakeItEasy.nuspec
output_folder:     Build
repo:              FakeItEasy/FakeItEasy
solution:          Source/FakeItEasy.sln
ssl_cert_file_url: http://curl.haxx.se/ca/cacert.pem
version:           1.21.0

integration_tests:
  Source/FakeItEasy.IntegrationTests/bin/Release/FakeItEasy.IntegrationTests.dll
  Source/FakeItEasy.IntegrationTests.VB/bin/Release/FakeItEasy.IntegrationTests.VB.dll

release_body:
  * **Changed**: _&lt;description&gt;_ - _#&lt;issue number&gt;_
  * **New**: _&lt;description&gt;_ - _#&lt;issue number&gt;_
  * **Fixed**: _&lt;description&gt;_ - _#&lt;issue number&gt;_
  
  With special thanks for contributions to this release from:
  
  * _&lt;user's actual name&gt;_ - _@&lt;github_userid&gt;_

release_issue_body:
  **Ready** when all other issues forming part of the release are **Done**.
  
  - [ ] run code analysis in VS in *Release* mode and address violations (send a regular PR which must be merged before continuing)
  - [ ] check build, update draft release in [GitHub UI](https://github.com/FakeItEasy/FakeItEasy/releases)
         including release notes, mentioning non-owner contributors, if any
&hellip;
</pre>

[Originally][original-vars], the `vars` task was hand-written, so
whenever we added a new variable we had to update the task. Not too
long ago, I added a new variable, and (surprisingly) remembered to update
`vars`. However, Adam noticed that I had put the `puts` statement in
the task in the wrong place, so the declaration order didn't match the
printed order. A small thing, but the small things matter.

So, we had a chat about the best way to present the
variables. Declaration order is attractive, but I pushed a different
approach: first, separating the variables with short values, such as
`assembly_info`, from variables with long values, such as
`release_body`. This keeps the short values from becoming lost in the
noise of the longer ones.  Second: sort lexicographically within the
groups, to aid scanning.

We came to an agreement, but as I started to make the change, I
thought, "Why make humans worry about this? Computers are good at
partitioning and sorting." So, after a quick search for something that
would allow printing of local Ruby variables, I found
[`local_variables`][local_variables], and rewrote the task:

{% highlight ruby %}
desc "Print all variables"
task :vars do
  print_vars(local_variables.sort.map { |name| [name.to_s, (eval name.to_s)] })  
end

def print_vars(variables)
  
  scalars = []
  vectors = []

  variables.each { |name, value|
    if value.respond_to?('each')
      vectors << [name, value.map { |v| v.to_s }]
    else
      string_value = value.to_s
      lines = string_value.lines
      if lines.length > 1
        vectors << [name, lines]
      else
        scalars << [name, string_value]
      end
    end
  }

  scalar_name_column_width = scalars.map { |s| s[0].length }.max
  scalars.each { |name, value| 
    puts "#{name}:#{' ' * (scalar_name_column_width - name.length)} #{value}"
  }

  puts
  vectors.each { |name, value| 
    puts "#{name}:"
    puts value.map {|v| "  " + v }
    puts ""
  }
end

{% endhighlight %}

Points of interest:

1. The task delegates to a function right away, to avoid creating new
  variables that would be found by `local_variables`. 
1. The first thing the method does is partition variables into
  "scalars", to be rendered on the same line as the variable name, and
  "vectors", which have multiple elements or lines, and are rendered
  _below_ the variable name.
1. As a bonus, the scalar variable names padded so the values can all land on a "tab stop"

Best of all, now we can add rake variables willy-nilly, with nary a
thought about printing them out. It just happens.


[adamralph]: http://adamralph.com/
[fakeiteasy]: http://fakeiteasy.github.io/
[nunit]: http://nunit.org/
[teamcity]: http://www.jetbrains.com/teamcity/
[original-vars]: https://github.com/FakeItEasy/FakeItEasy/blob/343a7a221906cc4c14971b46c3731c8a072eaf51/rakefile.rb#L36
[local_variables]: http://www.ruby-doc.org/core-2.0.0/Kernel.html#method-i-local_variables
