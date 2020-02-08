---
layout: post
title: expand your scope - you can dot-source more than just files 
comments: true
tags: Development, PowerShell
---
I'm working on a  <a href="../../../02/07/using-subversion-to-evangelize-powershell/">small project</a> that will require me to dot-source some PowerShell files in order to load their functions, aliases, and variables and make them available in a session. Actually, I have to do a little more than dot-source each file, but I'll keep the example simple to illustrate the wrinkle I ran into.

Suppose I have this file, <b>file-to-load.ps1</b>:

<pre><code class="powershell">Function Get-MyName
{
    Write-Output "Blair Conrad"
}</code></pre>

I dot-source it from the console, and everything's great:

<pre><code class="powershell">PS> . .\file-to-load.ps1
PS> Get-MyName
Blair Conrad</code></pre>

Because I'll be doing this over and over, and I want to manipulate the <code>.ps1</code> files a little more, I decide to wrap the dot-sourcing in a function, and call it.

<pre><code class="powershell">Function Load-File([string] $filename)
{
    . $filename
}</code></pre>

<pre><code class="powershell">PS> Load-File('.\file-to-load.ps1')
PS> Get-MyName
The term 'Get-MyName' is not recognized as the name of a cmdlet, function,
script file, or operable program. Check the spelling of the name, or if
a path was included, verify that the path is correct and try again.
At line:1 char:11
+ Get-MyName &lt;&lt;&lt;&lt;
    + CategoryInfo          : ObjectNotFound: (Get-MyName:String) [], CommandNotFoundException
    + FullyQualifiedErrorId : CommandNotFoundException</code></pre>

Not good. The <code>Get-MyName</code> function is loaded inside the scope of the <code>Load-File</code> function. It's only available as long as I'm inside <code>Load-File</code>.

I thought about modifying all the script files that were to be loaded, scoping each contained function, alias, and variable as <code>global</code>, but that would be a pain, and I'm not going to be the only one writing these files. Eventually, I came upon it: dot-source the <code>Load-File</code> function:

<pre><code class="powershell">PS> . Load-File('.\file-to-load.ps1')
PS> Get-MyName
Blair Conrad
</code></pre>

I'll admit I don't quite understand <em>why</em> it works, but for now, I'm content to know that it does.


