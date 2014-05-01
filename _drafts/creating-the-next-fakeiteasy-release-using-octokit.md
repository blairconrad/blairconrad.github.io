---
layout: post
title: "Preparing Your Next GitHub Project Release With Octokit"
comments: true
tags: 
      - releasing
      - octokit
      - ruby
---

At the Day Job, I work on a rather large enterprise application that
whose minor releases come out about twice a year, and larger releases
considerably less frequently.  As such, it was very refreshing to jump
on board the [FakeItEasy](http://fakeiteasy.github.io/) team, where
frequent small releases are de rigueur.

One problem with performing frequent small releases is that you frequently have to release. The act of releasing:

* steals time from other activities that could provide value, and
* is an opportunity to foul up and generate a flawed release

Of course, not releasing isn't a viable option, so we have to accept
some loss of time and some risk of introducing errors, but we can try
to minimize both.

<figure>
  <a href="https://github.com/FakeItEasy/FakeItEasy/issues/272"><img src="{{ site.image_dir }}/release_checklist.png"></a>
</figure>
