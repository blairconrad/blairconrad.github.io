---
layout: post
title: Animating Google Chrome Extension Page Action Icons
comments: true
tags:
    - AnimatedGIFs
    - ChromeExtensions
    - Development
    - JavaScript
    - setTimeout
---
I'm enjoying using (and working on) Library Lookup</a>, but I'm not entirely satisfied with the Page Action icons that pop up when searching, or when a book is found, or not found. In particular, I wanted a small animation while the search was ongoing, something like this: <img src="{{ site.image_dir }}/animated_search.gif" alt="" title="animated_search" width="12" height="16" class="alignnone size-full wp-image-565" />.

Unfortunately, the animated GIF didn't work - Google Chrome Extensions don't support them.

Briefly deterred, I regrouped and tried a different tack - something I like to call <em>A Bunch o' PNGs and Some Javascript</em>. First, I got myself three PNGs to display (okay, that's not entirely true - they're what I made the GIF from to begin with)
<ul>
<li style="list-style-image:url('{{ site.image_dir }}/searching_eye_right_16.png');">searching_eyes_right.png</li>
<li style="list-style-image:url('{{ site.image_dir }}/searching_eye_down_16.png');">searching_eyes_down.png</li>
<li style="list-style-image:url('{{ site.image_dir }}/searching_eye_left_16.png');">searching_eyes_left.png</li>
</ul>

Next, I needed a way to switch between the frames. I put the image names in an array, initialized an index, and wrote a small function that uses <a href="https://developer.mozilla.org/en/window.setTimeout">window.setTimeout</a> to switch to a new icon every 0.3 seconds.
{% highlight javascript %}
var searching_images = ['searching_eyes_down.png',
                        'searching_eyes_right.png',
                        'searching_eyes_down.png',
                        'searching_eyes_left.png'];

var image_index = 0;

var keep_switching_icon = true;
function rotateIcon()
{               
   if ( keep_switching_icon )
   {
      chrome.pageAction.setIcon({tabId: sender.tab.id, path: searching_images[image_index]});
      image_index = (image_index + 1) % searching_images.length;
      window.setTimeout(rotateIcon, 300);
   }
}
{% endhighlight %}

Then I start the rotation just before hitting the web server to see if the book's available and stop it when a result is found. Flipping the <code>keep_switching_icon</code> flag as soon as the search completes ensures that the animating thread doesn't overwrite a "found" or "not found" icon.

{% highlight javascript %}
window.setTimeout(rotateIcon, 300);
   
var xhr = new XMLHttpRequest();
xhr.open("GET", searchurl, true);
xhr.onreadystatechange = function() 
{
    if (xhr.readyState == 4) 
    {
       keep_switching_icon = false;
       if ( xhr.status != 200 )
       {
            chrome.pageAction.setIcon({tabId: sender.tab.id, path: 'my_book_error_19.png'});
            // other error handling
       }
      // process found and not found cases
};
xhr.send();
{% endhighlight %}

