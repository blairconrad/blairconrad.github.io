---
layout: post
title: IE binds to id attributes, or “How I learned to love var”
tags:
    - Ajax
    - Development
    - IE
    - JavaScript
    - LibraryHippo
---
<p>I recently converted the <a href="http://code.google.com/p/libraryhippo/">LibraryHippo</a> “Family Status” page to use AJAX to fetch individual card statuses, instead of having the server aggregate all the statuses and send the complete summary back to the user. It was fairly straightforward, with one notable exception – Internet Explorer. </p> 
<p><a href="{{ site.image_dir }}/working_ajax.png"><img title="AJAX LibraryHippo" height="191" width="244" alt="AJAX LibraryHippo" src="{{ site.image_dir }}/working_ajax_thumb.png" align="right" border="0" /></a>When using Firefox or Chrome, as soon as the page loaded, the user would see a list of cards that LibraryHippo was checking, complete with <a href="http://en.wikipedia.org/wiki/Throbber">throbbers</a>. As results came in, the matching progress line would disappear and other tables would fill in, holding the results – books that have to go back, holds ready for pickup, etc. I don't mind admitting that I was a little proud of my first foray into AJAXy web programming.</p> 
<p>The morning after I finished the update, a co-worker signed up. Unlike everyone else I knew, she used Internet Explorer. She hit the summary page and everything stalled. The progress list was populated, the throbbers were throbbing, and… that’s it. They just kept going. Oh, and a little indicator woke up in the status bar, saying that there was an error on the page: “<strong>Object doesn’t support this property or method</strong>”. The reported line numbers didn’t match my source file, but via judicious application of <code>alerts()</code>s, I was able to isolate the problem to a callback that’s executed on a successful card check to update a span that holds a row count:</p>
{% highlight javascript linenos=table %}
function refresh_table_count(table_selector)
{  
    count = $(table_selector + ' tbody tr').length;
    $(table_selector + ' thead #count').html(count);
}
{% endhighlight %}

<p>That seemed pretty innocuous, and not dissimilar from code that I had elsewhere in the <code>&lt;script&gt;</code> block. Quick web searches revealed nothing, so I resorted to cutting and renaming bits until I could see what was going on. I was down to an HTML body with a single table definition, and the function above. The error persisted. Suspicious, I renamed the <code>count</code> variable to <code>c</code>, and the problem disappeared.</p>

<p>At this point, I was convinced that IE’s Javascript interpreter reserved the <code>count</code> keyword for itself. I made this claim to a friend, who was skeptical. Eager to show him, I whipped up a quick example, and… it worked. There were no problems with the word <code>count</code>. I was stymied again, but not for long: my sample HTML file didn’t include an element with a &quot;count&quot; id. Once I added the count id, the sample broke.</p>

<p>It turns out that <a title="Rick Strahl - Internet Explorer Global Variable Blow ups" href="http://www.west-wind.com/weblog/posts/677442.aspx">IE is actually creating a global object that matches the item’s ID!</a> As Rick Strahl explains, the problem is a little worse than that, because the assignment on line 3 above should’ve overwritten the variable reference, but there’s “some whacky scoping going on”. </p>

<p>Workarounds:</p>

<ol>
  <li>do away with the temporary variable (possible in this case) </li>

  <li>rename the temporary variable (always possible, but lame) </li>

  <li>use more specific <code>id</code> attribute values (probably a good idea in any case) </li>

  <li>use the <a href="http://www.w3schools.com/js/js_variables.asp"><code>var</code> statement to</a> declare all variables – this is safest and probably the easiest to remember:</li>
</ol>

{% highlight javascript linenos=table %}
function refresh_table_count(table_selector)
{
    var count = $(table_selector + ' tbody tr').length;
    $(table_selector + ' thead #count').html(count);
}
{% endhighlight %}

<p>Now everything is working on the new page, and I've every confidence that <code>var</code> will help keep it so.
