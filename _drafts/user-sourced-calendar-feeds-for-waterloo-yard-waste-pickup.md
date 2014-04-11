---
layout: post
title: "User-Sourced Calendar Feeds for Waterloo Yard Waste Pickup" 
comments: true
tags:
    icalendar
    syndication
    waterloo
    off-topic
---

(Thanks to [Jon Udell][jonudell], whose insightful posts
are the only reason this would ever have occurred to me.)

I live in [Waterloo, Ontario][waterloo], a city with weekly
residential waste collection. In the warm months, there's an
additional biweekly (that's every 2 weeks, not twice a week)
collection of what's called _yard waste_: grass clippings, raked-up
leaves, tree branches, and so on.

People in my area (including me) have trouble remembering _which_
weeks are yard waste weeks.  This means that every two weeks I get to
see collections of plant material left at the curb outside people's
homes and then brought in a day or two later, only to reappear one
week later.

To compensate for my forgetfulness, I employ tools. Every year, at
the beginning of the warm season, I visit the Region of Waterloo's
website where I can learn about their [Yard waste residential
collection program][yard-waste-program]. Here I find links to two
PDFs: a [pretty version of the schedule for Waterloo][pretty], and an
["accessible"][accessible] version.

I look at one of those schedules, and I create a recurrning Google
Calendar event. Then my phone tells me on Sunday night whether to haul
the tree parts to the street. It works really well for me, and I get
to feel smug, looking at the yard waste sitting out along the street
on off weeks.

However, every year, I wish that the Region provided a
[.iCalendar][icalendar] feed or created a Google Calendar for me so I
wouldn't have to do this. But I don't do more than wish.

This year, I'm doing more. For starters, I created a few Google Calendars. One for me (and my fellow Monday-pickup people), and four for everyone else in Waterloo (and Cambridge).
The Region's web site gave me start and end weeks for pickups, so it was very easy to make a biweekly repeating event, using these Google Calendar settings:

<div class="images">
<img alt="Monday yard waste repeat schedule for Waterloo" src="{{ site.image_dir }}/yard-waste-repeat-details.png" style="border: 1px solid black">
</div>

Take them! Use them! If there's a problem, complain in the comments:

<table>
  <tr>
    <th>Day of Week</th>
    <th colspan="3">Waterloo and Cambridge</th>
  </tr>
  <tr>
    <td>Monday</td>
    <td><a href="https://www.google.com/calendar/ical/prgofd4tlk7as38mha1l6vktug%40group.calendar.google.com/public/basic.ics">iCal</a> (good for importing into Calendar apps)</td>
    <td><a href="https://www.google.com/calendar/feeds/prgofd4tlk7as38mha1l6vktug%40group.calendar.google.com/public/basic">XML</a></td>
    <td><a href="https://www.google.com/calendar/embed?src=prgofd4tlk7as38mha1l6vktug%40group.calendar.google.com&ctz=America/New_York">HTML</a></td>
  </tr>
  <tr>
    <td>Tuesday</td>
    <td><a href="https://www.google.com/calendar/ical/285agk21lcqiauhe36ekdscdvg%40group.calendar.google.com/public/basic.ics">iCal</a></td>
    <td><a href="https://www.google.com/calendar/feeds/285agk21lcqiauhe36ekdscdvg%40group.calendar.google.com/public/basic">XML</a></td>
    <td><a href="https://www.google.com/calendar/embed?src=285agk21lcqiauhe36ekdscdvg%40group.calendar.google.com&ctz=America/New_York">HTML</a></td>
  </tr>
  <tr>
    <td>Wednesday</td>
    <td><a href="https://www.google.com/calendar/ical/i7nb1lhk4q654f2nvgp18377c4%40group.calendar.google.com/public/basic.ics">iCal</a></td>
    <td><a href="https://www.google.com/calendar/feeds/i7nb1lhk4q654f2nvgp18377c4%40group.calendar.google.com/public/basic">XML</a></td>
    <td><a href="https://www.google.com/calendar/embed?src=i7nb1lhk4q654f2nvgp18377c4%40group.calendar.google.com&ctz=America/New_York">HTML</a></td>
  </tr>
  <tr>
    <td>Thursday</td>
    <td><a href="https://www.google.com/calendar/ical/rfpmnlo92dns1sp91m6rcc08qo%40group.calendar.google.com/public/basic.ics">iCal</a></td>
    <td><a href="https://www.google.com/calendar/feeds/rfpmnlo92dns1sp91m6rcc08qo%40group.calendar.google.com/public/basic">XML</a></td>
    <td><a href="https://www.google.com/calendar/embed?src=rfpmnlo92dns1sp91m6rcc08qo%40group.calendar.google.com&ctz=America/New_York">HTML</a></td>
  </tr>
  <tr>
    <td>Friday</td>
    <td><a href="https://www.google.com/calendar/ical/kbf75e38d537doohr2aola2b5g%40group.calendar.google.com/public/basic.ics">iCal</a></td>
    <td><a href="https://www.google.com/calendar/feeds/kbf75e38d537doohr2aola2b5g%40group.calendar.google.com/public/basic">XML</a></td>
    <td><a href="https://www.google.com/calendar/embed?src=kbf75e38d537doohr2aola2b5g%40group.calendar.google.com&ctz=America/New_York">HTML</a></td>
  </tr>
</table>

Next, I'm going to pester the Region, showing them how easy it was to
do this and to see if they'd be willing to carry on with the work next
year. If something comes of it, I'll let you know.

[jonudell]: http://blog.jonudell.net/
[waterloo]: http://www.waterloo.ca/
[yard-waste-program]: http://www.regionofwaterloo.ca/en/aboutTheEnvironment/seasonalservices.asp#yardwaste
[pretty]: http://www.regionofwaterloo.ca/en/aboutTheEnvironment/resources/YardWastebrochure2013-14WEBREV.pdf#yardwaste
[accessible]: http://www.regionofwaterloo.ca/en/aboutTheEnvironment/resources/2014YardWasteSCHEDULEODAWEB.pdf
[icalendar]: http://en.wikipedia.org/wiki/ICalendar
