---
layout: post
title: Waiting pays off again - Google App Engine gets Datastore retries
comments: true
tags: AppEngine, Development
---
<p>Sometimes when we wait a little, the universe provides for us. Last year, I was holding off taking LibraryHippo live because it's almost useless without daily notifications. At the time, Google App Engine had no scheduled tasks. I'd just resigned myself to soliciting users and setting up a cron job on one of my own computers to trigger the notifications, or use some other kind of hackery. Right after I made this decision, the Google App Engine team announced that Scheduled Tasks were available. Well, it's happened again.</p>
<p>I really enjoy working on the Google App Engine framework, but one of the more frustrating aspects (lately) has been the timeouts I get when reading from the Datastore. I've recently taken some steps that will reduce the impact on users, but was on the verge of implementing an automatic Datastore retry mechanism.
Fortunately, it looks like I may not have to, with the <a href="http://googleappengine.blogspot.com/2010/02/app-engine-sdk-131-including-major.html">arrival of App Engine SDK 1.3.1</a>:</p>

>"App Engine now automatically retries all datastore calls (with the exception of transaction commits) when your applications encounters a datastore error caused by being unable to reach Bigtable. Datastore retries automatically builds in what many of you have been doing in your code already, and our tests have shown it drastically reduces the number of errors your application experiences (by up to 3-4x error reduction for puts, 10-30x for gets)."

There are other Datastore improvements, including Datastore Query Cursors, and unlimited result set size for queries (previously the maximum was 1000). Also <a href="http://code.google.com/appengine/docs/python/tools/appstats.html">instrumentation</a> for the Python version of the SDK, and unit tests for Java.

I'm keen to try out the Python instrumentation, but I'm pretty sure I already know where my bottleneck is...
