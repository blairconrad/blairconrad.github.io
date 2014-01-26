---
layout: post
title: ReportGenerator indexing your whole drive? Check the case of your fullPaths.
comments: yes
tags: 
    - coverage
    - OpenCover
    - ReportGenerator
---

<p><em><strong>[Update on 2013-06-22:</strong> I should've
mentioned this a while ago, but the issue and patch I submitted were
accepted and built into ReportGenerator 1.7.3.0, so if you have
anything newer, you should be good.]</em></p>

Recently I was working on a project at the Day Job, using OpenCover
1.7.1.0 and ReportGenerator 4.0.804 to report my test coverage, [as is
my wont](/2011/12/15/best-all-around-net-coverage-tool-opencover),
when the report generation started taking figuratively
*forever*. <!--more--> Investigating, I saw something like

<pre>
found report files: D:/sandbox/project/src/buildlogs/temp_test_coverage/Project.UnitTest.coverage.xml
Loading report 'D:\sandbox\project\src\buildlogs\temp_test_coverage\Project.UnitTest.coverage.xml'
 Preprocessing report
  Indexing classes in directory 'D:\sandbox\project\src\Module1\SubPath\'
  Added coverage information of 370/370 auto properties to module 'Module1'
  Indexing classes in directory 'D:\'
</pre>

My D: drive isn't the hugest, but it's big enough, so that explained
the delay. And of course, I certainly didn't want anything above
D:\sandbox\project\src indexed.

I took a peek at my .coverage.xml file and the ReportGenerator code and until I found the offending lines

{% highlight xml linenos=table %}
<Module dhash="9A-A3-0A-C0-1D-57-BA-2A-C2-D4-5B-9E-08-DE-BD-2D-46-04-AF-32">
  <FullName>D:\Sandbox\project\src\Module\UnitTest\bin\Release\Module.dll</FullName>
  <ModuleName>Module</ModuleName>
  <Files>
    …
    <File uid="803" fullPath="D:\sandbox\project\src\Module\File1.cs" />
    <File uid="806" fullPath="D:\Sandbox\project\src\Module\File2.cs" />
    <File uid="808" fullPath="D:\sandbox\project\src\Module\File3.cs" />
    …
{% endhighlight xml linenos=table %}

Note the "Latin capital letter S" at the beginning of "Sandbox" on
line 7. All the other lines had a "Latin small letter S".  When
ReportGenerator goes looking for *.cs files to scan, it starts at the
directory whose name is the longest common prefix of all the
fullPaths. Because "S" isn't "s", it came up with "D:\".

I submitted <a
href="http://reportgenerator.codeplex.com/workitem/9773">an issue on
the ReportGenerator CodePlex project</a>, so maybe we'll see a fix
soon.

Of course I wondered "Why does the S differ for that entry?" but I
figured I'd look at one thing at a time, and locating the fix for
ReportGenerator was quicker.