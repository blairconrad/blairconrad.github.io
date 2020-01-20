---
layout: post
title: Using Subversion to Evangelize PowerShell
comments: true
tags: Development, PowerShell, Subversion
---
I've never been really comfortable with the Windows Command prompt - whenever I can, I grab <a href="http://www.cygwin.com/">Cygwin</a> to give myself a more familiar (and powerful) command-line environment. I really appreciate the tools included with the Unix command shells, as well as the easy composability of the utilities that come with Unix.

Unsurprisingly, I was immediately attracted to <a href="http://blogs.msdn.com/powershell/default.aspx">PowerShell</a> - a powerful replacement shell for Windows, with .NET integration, a Unix-like pipeline that works on objects rather than strings, and has plenty of built-in cmdlets. I installed it and tried to work. There were familiar commands (many of the Unix and Windows command names are aliased to their PowerShell equivalents), and these both helped and hindered - it was easy to find a command, but the options were slightly off, so the commands my fingers knew produced errors or unexpected results. Eventually I fell off the wagon, reverting to cmd.exe. Over the next year or so, I would return to PowerShell, only to stop using it again.

A few months ago, I was talking to the Guy in the Next Cubicle. He was also interested in PowerShell. We talked a little about the few scripts (neither of us had written new cmdlets) we'd made, and shared them. Having someone to talk to about PowerShell sparked something, and gave me the impetus to change my shortcuts to start PowerShell instead of cmd.exe. Unfortunately, sharing our scripts was awkward - usually via e-mail or instant messaging. In addition, as we improved our scripts, adding some to perform common tasks, we found the answers to some questions when people came for help was, "Well, if you had this PowerShell script, you'd just...", with no convenient way to get them the scripts.

Finally we decided to do something about it, and initiated a plan to help share our setup among our coworkers. We wanted a system that:
<ul>
        <li>was easy to adopt,</li>
	<li>made it easy to get and share scripts, and</li>
	<li>was customizable - so people could have different prompts, for example</li>
</ul>

Inspired by <a href="http://kitenet.net/~joey/svnhome/">Joey Hess's <i>keeping your life in svn</i></a>, we tried putting the whole profile directory under Subversion control. It was an easy choice, since everyone at the Day Job is already using Subversion to wrangle our source code.

<h4 id="getting_started">Getting Started</h4>
Getting started with the profile is almost as easy as running
<pre><code class="bat">cd %USERPROFILE%\My Documents
svn checkout http://svn.dayjob.com/path/to/PowerShellProfile/trunk WindowsPowerShell
</code></pre>

After this, the user will have a directory inside their My Documents directory that looks something like this:

<img src="{static}/images/powershellprofile2.png" alt="profile directory skeleton" title="PowerShellProfile" width="268" height="408" class="size-full wp-image-225" />

It's not quite usable, though. By default PowerShell doesn't allow scripts to be run, so the new profile will be of no benefit to users. To ease their pain, the profile directory contains a <b>setup_powershell.bat</b> which runs 
<pre><code class="bat">powershell -Command "Set-ExecutionPolicy RemoteSigned"
</code></pre>
After running setup_powershell.bat, all a user has to do is start PowerShell and they will benefit from the new profile.

<h4 id="windowspowershell">Inside the WindowsPowerShell Directory</h4>
The first item of note inside the WindowsPowerShellDirectory is the <b>Includes</b> directory, which is populated with `.ps1` files. Each `.ps1` file contains functions to be loaded into memory and made available for the user's session. 
At startup, each of these .ps1 files are each dot-sourced (using the <a href="{filename}2010-01-29-expand-your-scope-you-can-dot-source-more-than-just-files.md">dot-source from a function trick I talked about last time</a>).

Next, the <b>Scripts</b> directory, which is added to the user's <b>$env:PATH</b>. Each of the .ps1 files in the directory contains a standalone script that a user might choose to execute as they work. We have a number of Day&nbsp;Job-specific scripts as well as some Subversion helpers and two meta-scripts, designed to make it easier to work with the PowerShell profile.

Since new users won't be familiar with all the scripts in the profile, and because new scripts might be added at any time, we include a script to provide a quick synopsis of the available scripts: <b>Get-ProfileHelp</b>. It scans the `Scripts` directory, printing out, in an easy-to-read table,  the Synopsis from the top of each script.
<pre><code class="powershell">#<#
#.Synopsis
#  Get help for the PowerShellProfile scripts
##>
Get-ScriptDirectory | Get-ChildItem -include "*.ps1" -recurse
 | ForEach-Object {
    $name = $_.Name; $name = $name.Remove($name.Length-4)
    $synopsis = ""
    $content = (Get-Content $_.PSPath)
    for ($i = 0; $i -le ($content.length - 1); $i += 1)
    {
       if ( $content[$i] -like '*.Synopsis*' )
       {
           $synopsis = $content[$i+1].Substring(1).Trim()
           break
       }
    }
    $o = New-Object Object
    $o | Add-Member NoteProperty Name $name
    $o | Add-Member NoteProperty Synopsis $synopsis
    $o
} | Format-Table -AutoSize
</code></pre>
The `Get-ScriptDirectory` function just finds the location of the currently executing script. We'll see it later. Running the script gives output like this:

<pre>
Name                     Synopsis
----                     --------
Copy-Branch              Copy an SVN branch, and optionally switch to the new branch
Get-ProfileHelp          Get help for the PowerShellProfile scripts
Get-SslCertificate       Load and display an SSL Certificate from a host
Import-ResharperSettings Import Resharper 4.5 settings from a file
Merge-Branch             Merge SVN commits back into the current working directory
Switch-Branch            Switch to a new SVN branch
Update-Profile           Get the latest version of the PowerShell profile from SVN
</pre>


Rather than forcing users to navigate to the profile directory and run an `svn` command, the <b>Update-Profile.ps1</b> script will automatically update the profile source:
<pre><code class="powershell">#<#
# .SYNOPSIS
#     Get the latest version of the PowerShell profile from SVN
##>
svn update (Split-Path $profile)
</code></pre>

<h4 id="user_profile_directories">User Profile Directories</h4>
In addition to the `Includes` and `Scripts` directories, each user of the PowerShell profile can have their own directory full of customizations. The name of the directory is taken from the <b>$env:USERNAME</b> variable. On startup, if the directory exists, any `Include` and `Scripts` directories are processed - being dot-sourced or added to the path, respectively. This allows users to have their own personal scripts and functions. In addition, the <b>profile.ps1</b> from the directory is dot-sourced.

If a user runs PowerShell and doesn't already have a profile directory, a welcome message is printed to the screen, explaining basic usage of the profile. Then a profile directory is created and populated with an empty `profile.ps1` to get the user started and to keep them from being welcomed again.

Some users choose to commit their personal profile directories to the repository, and some don't - there's no requirement either way. If someone chose, they could even use an `svn:externals` on the `WindowsPowerShell` directory and host their personal directory in another part of the repository or even a different repository.

<h4 id="putting_it_all_together">Putting it All Together</h4>
Finally we see the <b>Microsoft.PowerShell_profile.ps1</b> file that orchestrates all this:
<pre><code class="powershell"># Will turn on extra output to help debug profile-loading.
# Don't check in as "true"
$verbose = $false

# A convenience function to get the directory the current script lives in
# - useful for importing from relative paths
function Get-ScriptDirectory
{
  $Invocation = (Get-Variable MyInvocation -Scope 1).Value
  Split-Path $Invocation.MyCommand.Path
}

function Include-ProfileDirectory([string] $directory)
{
    # Load every file in the Includes subdirectory -
    # hopefully they can be loaded in any order.
    # The Includes directory should contain files that define functions and 
    # filters to be executed later, but not scripts that need to do
    # something when the file is sourced.
    if ( Test-Path ($directory + '\Includes') )
    {
        Get-ChildItem -Path:($directory + '\Includes') -Filter:*.ps1 | ForEach-Object {
            if ( $verbose )
            {
                Write-Output ("importing " + $_.PSPath)
            }
            . $_.PSPath
        }
    }

    # The Scripts directory should contain PowerShell scripts that someone
    # might want to be executed, so we'll add it to our path.
    if ( Test-Path "$directory\Scripts" )
    {
        $env:PATH = "$($env:PATH);$directory\Scripts"
    }
}

# dot-source the Include-ProfileDirectory function. If we run it 
# directly,  all the included functions will be scoped inside the
# Include-ProfileDirectory command, and inaccessible to the user.
. Include-ProfileDirectory(Get-ScriptDirectory)

# Look for user-specfic customizations. If they're there, load them.
$userProfileDir = ((Get-ScriptDirectory) + '\' + $env:USERNAME)
if ( Test-Path $userProfileDir )
{
    if ( $verbose )
    {
        Write-Output "including $userProfileDir"
    }
    . Include-ProfileDirectory($userProfileDir)

    $userProfile = ($userProfileDir + '\profile.ps1')
    if ( Test-Path $userProfile )
    {
        . $userProfile
    }
}
else
{
    Write-Host -foregroundColor yellow -backgroundColor darkblue @"

Welcome to the DayJob PowerShell Profile.  It looks like this is your
first time here, so I'll create a new profile for you. This profile
will be called

   $userProfile

If you want to customize your PowerShell experience, you can edit this
file. Eventually you may want to modify files in the containing directories,
but keep in mind that those changes will affect other users.

Have fun!

"@

    New-Item -path  $userProfile -itemType "file" -Force > Out-Null
}
</code></pre>