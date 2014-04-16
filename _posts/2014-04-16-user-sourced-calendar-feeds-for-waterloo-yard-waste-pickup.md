---
layout: post
title: "User-Sourced Calendar Feeds for Waterloo Yard Waste Pickup" 
comments: true
tags:
    icalendar
    syndication
    waterloo
    diversions
---

(Thanks to [Jon Udell][jonudell], whose insightful posts
are the only reason this would ever have occurred to me.)

I live in [Waterloo, Ontario][waterloo], a city with weekly
residential waste collection. My collection day is Monday. In the warm months, there's an
additional biweekly (that's every 2 weeks, not twice a week)
collection of what's called _yard waste_: grass clippings, raked-up
leaves, tree branches, and so on.

People in my area (including me) have trouble remembering _which_
weeks are yard waste weeks.  This means that every two weeks I get to
see collections of plant material left at the curb outside people's
homes and then brought in a day or two later, only to reappear the
next week.

I use tools to augment my memory. Every year, at
the beginning of the warm season, I visit the Region of Waterloo's
website where I can learn about their [Yard waste residential
collection program][yard-waste-program]. Here I find links to two
PDFs: a [pretty version of the schedule for Waterloo][pretty], and an
["accessible"][accessible] version.

I look at one of those schedules, and I create a recurrning Google
Calendar event. Then my phone tells me on Sunday night whether to haul
the tree parts to the street. It works really well.

However, every year, I've wished that the Region provided an
[.iCalendar][icalendar] feed or created a Google Calendar for me so I
wouldn't have to do this. But I haven't done more than wish.

This year, I'm doing more. For starters, I created a few Google
Calendars. One for me (and my fellow Monday-pickup people), and four
for everyone else in Waterloo (and Cambridge).  The Region's web site
gave me start and end weeks for pickups, so it was very easy to make a
biweekly repeating event, using these Google Calendar settings:

<div class="figure">
<img alt="Monday yard waste repeat schedule for Waterloo" src="{{ site.image_dir }}/yard-waste-repeat-details.png">
</div>

Lo and behold, it shows up in my calendar:

<div class="figure">
<img alt="Monday yard waste shown in Google Calendar" src="{{ site.image_dir }}/yard-waste-shown-in-calendar.png">
</div>

I created the Tuesday through Friday calendars by making the obvious
modification to the schedule above.

I put
[all the calendars on a separate page][yard-waste-collection-schedule]
that I intend to maintain until the Region provides replacements. Or I
move. Go! Get one for your collection day.

Next, I'm going to pester the Region, showing them how easy it was to
do this and to see if they'd be willing to carry on with the work next
year. If something comes of it, I'll let you know.

[jonudell]: http://blog.jonudell.net/
[waterloo]: http://www.waterloo.ca/
[yard-waste-program]: http://www.regionofwaterloo.ca/en/aboutTheEnvironment/seasonalservices.asp#yardwaste
[pretty]: http://www.regionofwaterloo.ca/en/aboutTheEnvironment/resources/YardWastebrochure2013-14WEBREV.pdf#yardwaste
[accessible]: http://www.regionofwaterloo.ca/en/aboutTheEnvironment/resources/2014YardWasteSCHEDULEODAWEB.pdf
[icalendar]: http://en.wikipedia.org/wiki/ICalendar
[yard-waste-collection-schedule]: {{ site.url }}/yard-waste-collection-schedule/
