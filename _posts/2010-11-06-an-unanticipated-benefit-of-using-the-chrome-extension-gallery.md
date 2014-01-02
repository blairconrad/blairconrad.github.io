---
layout: post
title: An unanticipated benefit of using the Chrome Extension Gallery
tags:
    - ChromeExtensions
    - Development
---
I've written 3 Google Chrome Extensions. The first two were for use at the Day Job, so I initially hosted them on an internal server. Eventually I moved them out to the <a href="https://chrome.google.com/extensions">Chrome Extension Gallery</a>. There are a few benefits to doing this over self-hosting:

<ul>
<li>better publicity - as it's the prime location for extensions, people will go here looking for them, and they may find your extension</li>
<li>Google maintains the site, so uptime's pretty good</li>
<li>the extension gallery maintains the <a href="http://code.google.com/chrome/extensions/autoupdate.html#H2-2">update manifest</a></li>
</ul>

The first two benefits aren't a big deal for the Day Job extensions. We've a team to keep the servers up, and internal advertising channels. Mostly I enjoyed being freed of the monotony of generating new update manifests.

<h2>A bonus benefit</h2>
Last night a new benefit reached out and figuratively grabbed me by the lapels and shook me. I got mail from Google Extensions. They wanted to warn me about a problem with my extension. Sort of. Here it is:

> From:	<b>Google Extensions</b>  
> To:	<b>Google Extensions</b>  
> Subject:	<b>Important: Your extension is broken for all Chrome users - Here's how to fix it</b>  
> 	
> Hello,  
> 
> You are receiving this mail because you are the owner of an extension
> on chrome.google.com/extensions that was broken by a recent update to
> Chrome. This affects ALL users of Chrome, so it is something you
> should fix as soon as possible.
> 
> Fortunately, the fix is very simple.
> 
> In earlier versions of Chrome, the following syntax was supported:
> 
> {% highlight html %}<script src="example.js">{% endhighlight %}
>
>In current versions, this is no longer legal and must be changed to:
> {% highlight html %}<script src="example.js"></script>{% endhighlight %}
> All you have to do is replace any instances of this pattern in your
extension and re-upload, and it should work again.
> 
> We try very hard to avoid ever making breaking changes to the
> extension system, but in this case we did not notice it until the
> release had already been shipped. Since this is affecting users right
> now, we thought you'd appreciate details on what happened, and how to
> fix it yourself immediately.
> 
> Thanks,
> 
> -- The Chrome extensions team

There's a new version of Chrome. It has a flaw, or at least a regression - the old syntax for including  a script isn't supported. I'm a little disappointed that that change went in, but I'll get over it.

The point is, once a bug was discovered, Google scanned all the extensions, identified those that were affected by the bug, and alerted the owners. I appreciate that they took this step. It's much better than just letting us sit around, waiting for users to tell us that our extension is broken. 

I wish at the Day Job we had this kind of ability. As things are, when a problem is discovered at a customer's site, we don't have an automated way of investigating their installation to see if their data will be problematic, or if the product wizards they've written are going to cause a problem. We sometimes obtain copies of sites' databases and configuration settings to diagnose a pernicious bug or to evaluate whether a proposed upgrade will be harmful. Unfortunately these instances are infrequent and are always a manual process.

<h2>At the risk of seeming ungrateful</h2>
I appreciate the notification, and will get right on the update so my user isn't affected. However, if I had my druthers, it would have been nice to have been told
<ul>
<li><i>which</i> extensions are affected - Google've already looked at all the extension. They know which ones I need to change. Save me the trouble of grepping. Of course, this would necessitate customized e-mails, rather than an all-purpose message.</li>
<li>which versions of Chrome were affected (I mean something more specific than "current versions")</li>
<li>whether this bug is fixed, or if it's going to be fixed in the future. I'm left not knowing if this is a temporary aberration, or if I need to use the <code><script></script></code> syntax forever</li>


