---
layout: page 
title: Archive
permalink: /archive/
---

{% for post in site.posts %}
    {% capture postmonth %}{{ post.date | date: "%B" }}{% endcapture %}
    {% capture postyear %}{{ post.date | date: "%Y" }}{% endcapture %}
    {% if postyear != year %}
        {% assign month = postmonth %}
        {% assign year = postyear %}
        {% if forloop.first %}
        {% else %}
</ul>
        {% endif %}
<h2 id = "{{ year }}">{{ year }}</h2>
<ul>
    {% endif %}
  <li>{{ post.date | date: "%Y-%m-%d" }} <a href="{{ post.url }}">{{ post.title }}</a> </li>
{% endfor %}

<!--
<ul>
{% for post in site.posts %}
<li>
       {{ post.date | date: "%Y-%m-%d" }} <a class="title" href="{{ post.url }}">{{ post.title }}</a>
</li>
{% endfor %}
</ul>


-->