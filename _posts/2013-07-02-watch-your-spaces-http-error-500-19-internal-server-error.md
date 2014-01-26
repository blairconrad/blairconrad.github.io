---
layout: post
title: Watch your spaces - HTTP Error 500.19 - Internal Server Error
comments: true
tags:
    - 500-19 
    - iis 
    - iis7
---
Late last week at the Day Job, a colleague came to me with a problem. The web service he was trying to hit was throwing an error he'd never seen before:

<blockquote style="color:#CC0000;">
HTTP Error 500.19 - Internal Server Error
The requested page cannot be accessed because the related configuration data for the page is invalid.
</blockquote>

I'd never seen it before either, at least not in this exact incarnation. Take a look

<a href="{{ site.image_dir }}/500-191-internal-server-error.png"><img style="display: block; margin-left: auto; margin-right: auto;" src="{{ site.image_dir }}/500-191-internal-server-error-small.png" alt="screenshot of 500.19 error" width="500" height="334" /></a>

<!--more-->

In case the text isn't so clear, here are the details:

<table align="center" border="1" style="border-collapse:collapse;border:1p black;width:50%;margin-left:25%;margin-right:25%;">
<col style="background-color:#CBE1EF;" />
<tr><th style="border:none;padding:1px 3px;">Module</th><td style="border:none;padding:1px 3px;">IpRestrictionModule</td></tr>
<tr><th style="border:none;padding:1px 3px;">Notification</th><td style="border:none;padding:1px 3px;">BeginRequest</td></tr>
<tr><th style="border:none;padding:1px 3px;">Handler</th><td style="border:none;padding:1px 3px;">WebServiceHandlerFactory-Integrated-4.0</td></tr>
<tr><th style="border:none;padding:1px 3px;">Error Code</th><td style="border:none;padding:1px 3px;">0x80072af9</td></tr>
<tr><th style="border:none;padding:1px 3px;">Requested URL</th><td style="border:none;padding:1px 3px;">http://localhost:80/My.Virtual.Directory/Service.asmx</td></tr>
<tr><th style="border:none;padding:1px 3px;">Physical Path</th><td style="border:none;padding:1px 3px;">C:\inetpub\wwwroot\My.Virtual.Directory\Service.asmx</td></tr>
<tr><th style="border:none;padding:1px 3px;">Logon Method</th><td style="border:none;padding:1px 3px;">Not yet determined</td></tr>
<tr><th style="border:none;padding:1px 3px;">Logon User</th><td style="border:none;padding:1px 3px;">Not yet determined</td></tr>
</table>

The errors suggested that we have problems with the configuration file, but the web.config was present (and well-formed), and there were no obvious permission problems, so it seems the file was being read. There was nothing in the event logs. Web searches yielded nothing that matched the <code>0x80072af9</code> error code or the description of the error. Even ERR.exe, recommended by <a href="http://blogs.iis.net/webtopics/archive/2010/03/08/troubleshooting-http-500-19-errors-in-iis-7.aspx">Troubleshooting HTTP 500.19 Errors in IIS 7</a>, failed me.

Fortunately, there were sibling virtual directories on the server, and they were working fine, even under the same App Pool. I knew that this virtual directory, unlike the others, restricted access to a whitelist of IP addresses. So, I changed the <code>security/ipSecurity</code> node's <code>allowUnlisted</code> to <code>true</code>, just in case for some reason the clients' IP addresses weren't being detected properly. No change.

Frustrated, I removed the whole <code>security</code> node. The service worked!

So I took a closer look at the node:

{% highlight xml %}
<security>
  <ipSecurity allowUnlisted="false">
    <add ipAddress="127.0.0.1" allowed="true" />
    <add ipAddress="1.2.3.4 " allowed="true" />
  </ipSecurity>
</security>
{% endhighlight xml %}


Check out that "1.2.3.4" ipAddress. Now check it again. It's actually
"1.2.3.4<b> </b>", with a space at the end. (I bolded the space there,
just so you wouldn't miss it.) It seems that this messes up the IP
parsing, and IIS is completely flummoxed. Remove the space, and all is
well.
