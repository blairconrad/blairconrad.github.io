---
layout: post
title: "App Engine + External Authentication: Exposing Handlers to Cron, Tasks, and Admins" 
comments: true
tags:
    - AppEngine
---

Since Google is [deprecating OpenID 2.0 support][deprecating], I
decided to update [LibraryHippo][libraryhippo] to authenticate via
[OAuth 2.0][oauth], which is a story in itself, but I'm here to talk
about what happened next.

LibraryHippo has a set of handlers that are accessed primarily via the
[Cron][cron] and [Task Queue][task] mechanisms, but every once in a
while need to be triggered ad hoc by a human administrator. Up 'til
now, these request handlers were protected from the rabble by
[requiring administrator status via the application's app.yaml][requireadmin]. Unfortunately,
externally-authenticated users have no special standing within App
Engine, so this restriction had to be relaxed.

My first thought was to remove the restriction from app.yaml and check
for access in the handler like so:

<pre><code class="python">if (users.is_current_user_admin() or
    self.is_external_user_admin()) # application code that understands the logged-in users
    # do stuff
else:
    self.abort(403)</code></pre>

Unfortunately, this fails miserably. When the handler is executed by a
task or cron job, `users.is_current_user_admin` returns `False`.

This behaviour seems not to be widely reported; I couldn't find it
mentioned in the [App Engine issues list][issues], but a web search
eventually turned up
[App Engine: Google fails users.is_current_user_admin() test][bendavies]
by Ben Davies, an article written nearly 5 years ago.

In this article, Mr. Davies suggests that the best alternative to
`users.is_current_user_admin` is to "check the easily spoofed request
user-agent". I was skittish of this approach, especially since Google
is now recommending checking `X-AppEngine-Cron` when
[securing URLS for cron][securingcron]. The App Engine documentation
explains how X-AppEngine-Cron is protected against spoofing, but I'm
still uneasy.

I ended up taking a different approach. I added two routes for the
affected handlers. One route is in the old "admin" subdirectory
(subpath?) and the other in a new one for system commands,
"system". The latter is secured in the app.yaml, just as before. Thus
I have:

<pre><code class="yaml"># in app.yaml
- url: /system/.*
  script: libraryhippo.application
  login: admin</code></pre>

<pre><code class="python"># in the application's Python source
handlers = [
    # other handlers
    ('/admin/notify/(.*)$', Notify),
    ('/system/notify/(.*)$', Notify),
    ]

# and later, in the Notify handler
    request_path = urlparse.urlsplit(self.request.url).path
    if (self.is_external_user_admin() or
        not request_path.startswith('/admin/'))
        # do stuff
    else:
        self.abort(403)</code></pre>

Thus the handler is executed if the user has admin rights or the URL
isn't locked down by virtue of being below '/admin/'. The '/system/'
URLs are all assumed to be protected by the app.yaml setting.

Perhaps this is technically no better than checking a header in the
request, but it works for me, at least until I see what happens with
[Issue 11576: have users.is_current_user_admin return true for tasks and cron jobs][issue11576].

[deprecating]: https://developers.google.com/accounts/docs/OpenID2
[libraryhippo]: /tags/#LibraryHippo-ref
[oauth]: http://oauth.net/
[cron]: https://cloud.google.com/appengine/docs/python/config/cron
[task]: https://cloud.google.com/appengine/docs/python/taskqueue/
[requireadmin]: https://cloud.google.com/appengine/docs/python/config/appconfig#Python_app_yaml_Requiring_login_or_administrator_status
[issues]: https://code.google.com/p/googleappengine/issues/list?can=1
[bendavies]: http://www.learningtechnicalstuff.com/2010/01/app-engine-google-fails.html
[securingcron]: https://cloud.google.com/appengine/docs/python/config/cron#Python_app_yaml_Securing_URLs_for_cron
[issue11576]: https://code.google.com/p/googleappengine/issues/detail?id=11576
