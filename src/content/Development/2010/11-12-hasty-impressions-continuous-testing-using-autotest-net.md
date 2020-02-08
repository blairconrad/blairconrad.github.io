---
layout: post
title: Hasty impressions&#58; Continuous testing using AutoTest.NET
comments: true
tags: .NET, AutoTest.Net, HastyImpressions, Testing
---
<a href="http://abdullin.com/journal/2010/11/11/mighty-moose-smart-continuous-unit-tests-for-net-and-mono.html">Rinat Abdullin recently posted about Mighty Moose and AutoTest.NET</a>, two projects for continuous testing in the .NET/Mono space. My interest was immediately piqued, as I'm a huge fan of continuous testing. I've been using <a href="http://codespeak.net/py/dist/test/">py.test</a> to run my Python unit tests for years now, almost solely because <a href="http://codespeak.net/py/dist/test/features.html#looping-on-the-failing-test-set">it offers this feature</a>.

I'm taking a look at <a href="https://github.com/acken/AutoTest.Net">AutoTest.Net</a> first. Mostly because it's free. If I'm going to use something at home, it won't be for-pay, and the Day Job has been notoriously slow at shelling out for developer tools.

<strong>Update</strong>: there was a bug that had been fixed on trunk, but not in the installer that I used. <a href="{filename}../2010\/11-14-autotest-net-updated-now-and-then-notices-broken-builds.md">AutoTest.Net is better at detecting broken builds</a> than I report below. 

<h2>Setting up AutoTest.NET</h2>
Download and installation were straightforward. I opted to use the Windows installer package, <a href="https://github.com/downloads/acken/AutoTest.Net/AutoTest.Net-v1.0.1beta%20(Windows%20Installer).zip">AutoTest.Net-v1.0.1beta (Windows Installer).zip</a>. I just unzipped, ran the MSI, let it install both VS&nbsp;2008 and VS&nbsp;2010 Add-Ins (the other components are required, it seems), and that was that.

Then I cracked open the configuration file (at <code>c:\Program Files\AutoTest.Net\AutoTest.config</code>). I just changed two entries:
<ul>
<li><code>BuildExecutable</code>, and</li>
<li><code>NUnitTestRunner</code></li>	
</ul>

That's it. Well, for the basic setup.

<h2>Running the WinForms monitor</h2>

I opened a command prompt to the root of a small project and ran the WinForms monitor, telling it to look for changes in the current directory.
<pre><code class="bat">& 'C:\Program Files\AutoTest.Net\AutoTest.WinForms.exe' .</code></pre>

The application started, presenting me with a rather frightening window

<div class="images">
<a href="{static}/images/autotestwinform.png"><img src="{static}/images/autotestwinform.png" alt="AutoTestWinForm" title="([^"]+)" width="596" height="231" class="aligncenter size-full wp-image-767" /></a>
</div>

I mean, it makes sense. I have neither built nor run yet, so what did I expect? Still, I was taken aback by the plainness of it. Only temporarily daunted, I then hit the tiny unlabelled button in the northeast corner and got a new window. This was less scary.

<div class="images"><a href="{static}/images/autotest-winforms-messages.png"><img src="{static}/images/autotest-winforms-messages.png" alt="autotest winforms messages" title="autotest winforms messages" width="455" height="212" class="aligncenter size-full wp-image-782" /></a>
</div>

Everything seemed to be in order. I <i>hadn't</i> specified MS Test or XUnit runners, nor a code editor. It says it's watching my files. So let's test it.

<h2>Mucking with the source</h2>
It's supposed to watch my source changes and Do The Right Thing. Let's see about that.

<h3>A benign modification to one test file</h3>
I changed the text in one of my test files. No functionality was changed - it was purely cosmetic. AutoTest.Net noticed, rebuilt the solution, and ran the tests! Pretty slick. Things moved quickly, but here's what I saw from the application:

<div class="images">
<a href="{static}/images/innocuos-test-change-building.png"><img src="{static}/images/innocuos-test-change-building.png" alt="innocuous test change building" title="innocuous test change building" width="538" height="231" class="aligncenter size-full wp-image-788" /></a>
<a href="{static}/images/innocuos-test-change-testing-done.png"><img src="{static}/images/innocuos-test-change-testing-done.png" alt="innocuous test change testing done" title="innocuous test change testing done" width="538" height="231" class="aligncenter size-full wp-image-787" /></a>
</div>

<h3>A benign modification to one "core" file</h3>
Next I changed the text in one of the core files - this file is part of a project that's referenced by the BookFinder GUI project, and the test project. Again, this was a cosmetic change only, just to see what AutoTest.NET would do.
It did what it should - built the three projects and ran the tests. See?

<div class="images">
<a href="{static}/images/innocuous-core-change-testing-done.png"><img src="{static}/images/innocuous-core-change-testing-done.png" alt="innocuous core change testing done" title="innocuous core change testing done" width="538" height="231" class="aligncenter size-full wp-image-790" /></a>
</div>

<h3>A core change that breaks a test</h3>
So, now I'll modify the core code in a way that breaks a test.
It picks up the change, builds, tests, and does a really nice job of showing me the failure. I see the test that failed, and when I click it, am presented with the stack trace, including hyperlink to the source. 

<div class="images">
<a href="{static}/images/breaking-test-change-after-test.png"><img src="{static}/images/breaking-test-change-after-test.png" alt="breaking test change after test" title="([^"]+)" width="602" height="335" class="aligncenter size-full wp-image-794" /></a>
</div>

Unfortunately, clicking the hyperlink didn't go so well:

<div class="images">
<a href="{static}/images/breaking-test-change-edit-source.png"><img src="{static}/images/breaking-test-change-edit-source.png" alt="breaking test change edit source" title="([^"]+)" width="603" height="373" class="aligncenter size-full wp-image-793" /></a>
</div>

That was a little disappointing. On the brighter side, hitting "Continue" did continue, with no seeming ill-effects.

<h3>Redemption</h3>
Confession time. I hadn't checked the <code>CodeEditor</code> section of the configuration file. As it turns out, it had a slightly different path to my devenv than the correct one. I fixed up the path and tried again. This time, clicking on the hyperlink opened devenv at the right spot. 

So the problems was <i>ultimately</i> my fault, but I can't help but wish for more graceful behaviour - how about a "I couldn't find your editor" dialogue? Ah, well. The product's young. Polish will no doubt come.

I repaired the code that broke the tests, and AutoTest.Net was happy again after rebuilding and rerunning the tests.

<h3>Syntax Error</h3>
For my last test, I decided to actually break the compile. This was kind of disappointing. It claimed to run the 3 builds and the tests, and said that everything passed. I'm not sure why this would be - I was really hoping for an indication that the compilation failed, but nope. Everything was rainbows and puppies. <strong>Spurious rainbows and puppies.</strong>

<h2>The VS Add-In</h2>
There's an add-in. You can activate it under the "Tools" menu. It looks and behaves like the WinForms app.

<h2>The Console Monitor</h2>
I am used to running py.test in the console, so I thought I'd check out AutoTest's console monitor next. I started it up, made a benign change, and then made a test-breaking change. Here's what I saw:

<pre>
[Info] 'Default' Starting up AutoTester
[Info] 'AutoTest.Console.ConsoleApplication' Starting AutoTest.Net and watching "." and all subdirectories.
[Warn] 'AutoTest.Console.ConsoleApplication' XUnit test runner not specified. XUnit tests will not be run.
[Info] 'AutoTest.Console.ConsoleApplication' Tracker type: file change tracking
[Warn] 'AutoTest.Console.ConsoleApplication' MSTest test runner not specified. MSTest tests will not be run.
[Info] 'AutoTest.Console.ConsoleApplication'
[Info] 'AutoTest.Console.ConsoleApplication' Preparing build(s) and test run(s)
[Info] 'AutoTest.Console.ConsoleApplication' Ran 3 build(s) (3 succeeded, 0 failed) and 2 test(s) (2 passed, 0 failed, 0 ignored)
[Info] 'AutoTest.Console.ConsoleApplication'
[Info] 'AutoTest.Console.ConsoleApplication' Preparing build(s) and test run(s)
[Info] 'AutoTest.Console.ConsoleApplication' Ran 3 build(s) (3 succeeded, 0 failed) and 2 test(s) (1 passed, 1 failed, 0 ignored)
[Info] 'AutoTest.Console.ConsoleApplication' Test(s) failed for assembly BookFinder.Tests.dll
[Info] 'AutoTest.Console.ConsoleApplication'     Failed -> BookFinder.Tests.BookListViewModelTests.FindClick_WithTitleG_FindsEndersGame:
[Info] 'AutoTest.Console.ConsoleApplication'
</pre>

Not bad, but I have no stack trace for the failed test. Just the name. I'm a little sad to lose  functionality relative the WinForms runner. I know I wouldn't be able to click on source code lines, but still.

<h2>Gravy - Hooking up Growl</h2>
Undeterred by the disappointing performance in the Syntax Error test, I soldiered on. I use Growl for Windows for notifications, and I was keen to see the integration. I went back to the configuration file and input the <code>growlnotify</code> path. While I was there, I set <code>notify_on_run_started</code> to <code>false</code> (after all, I know when I hit "save"), and <code>notify_on_run_completed</code> to <code>true</code>. Then I fixed my compile error and saved the file.
In addition to the usual changes to the output window, I saw some happy toast:

<div class="images">
<a href="{static}/images/autotest-growl.png"><img src="{static}/images/autotest-growl.png" alt="autotest growl" title="([^"]+)" width="249" height="83" class="aligncenter size-full wp-image-798" /></a>
</div>

Honestly, with a GUI or text-based component around, I'm not sure how much benefit this will be, but I guess I can minimize the main window and so long as tests keep passing, I can get some feedback. Still it's kind of fun.

<h2>Impressions</h2>
I really like the idea of this tool. I love the idea of watching my code and continuously running the tests. The first steps are very good - I like the clickonable line numbers to locate my errors, and I think the Growl support is cute, but probably more of a toy than an actual useful feature. 

<h3>Will I Use It?</h3>
Not now, and probably never at the Day Job. The inability to detect broken builds is pretty disappointing.
Also, at work, I have <a href="http://www.jetbrains.com/resharper/features/unit_testing.html">ReSharper to integrate my unit tests</a>. I've bound "rerun the previous test set" to a key sequence, so it's just as easy for me to trigger as it is to save a file.

At home? Maybe. If AutoTest.Net starts noticing when builds fail, then I probably will use it when I'm away from ReSharper and working in .NET. 
