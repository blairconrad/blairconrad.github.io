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

One problem with performing frequent small releases is that you
frequently have to release. The act of releasing

* steals time from other activities that could provide value, and
* is an opportunity to foul up and generate a flawed release

Of course, not releasing isn't a viable option, so we have to accept
some loss of time and some risk of introducing errors, but we can try
to minimize both.

One way to improve productivity and increase consistency is to use
[checklists][checklists].  When I showed up at FakeItEasy Enterprises,
each new release was described by an issue that included a
comprehensive checklist, such as the one:

<figure>
  <a href="https://github.com/FakeItEasy/FakeItEasy/issues/272"><img src="{{ site.image_dir }}/release_checklist.png"></a>
</figure>

I found this extremely helpful as I made my first releases. The main
benefit was that the list of steps ensured that I didn't forget
anything.  However, the list was fairly long, at 15 steps, in spite of
efforts to streamline the process. So more recently I find myself chafing at repeating some tasks.

While it would be nice to just push a button and have the release
done, there will always be some manual work&mdash;I wouldn't trust a
robot to generate a tweet that correctly thanked contributors, for
example. Still, I went looking for some steps that can be
streamlined.

For my first task, I focused on creating the next GitHub release,
milestone, and release issue. These tasks don't really require any
intelligence, other than picking the next release number, and all can
be accomplshed using the [GitHub API][githubapi]. Another benefit of
grouping these tasks in a Rake task is that creating the next GitHub
release while closing the current one means the next release draft can
be edited as contributing issues are marked as done, ensuring that
release notes and thank-yous are accurate.

The Rake task is called `create_milestone` and accepts a
`milestone_version` as an argumentent.

{% highlight ruby %}
desc "create new milestone, release issue and release"
task :create_milestone, :milestone_version do |t, args|
  require 'octokit'

  ssl_cert_file = get_temp_ssl_cert_file(ssl_cert_file_url)

  client = Octokit::Client.new(:netrc => true)

  release_description = args.milestone_version + ' release'

  puts "Creating milestone '#{args.milestone_version}'..."
  milestone = client.create_milestone(
    repo,
    args.milestone_version,
    :description => release_description
    )
  puts "Created milestone '#{args.milestone_version}'."

  puts "Creating issue '#{release_description}'..."
  issue = client.create_issue(
    repo,
    release_description,
    release_issue_body,
    :labels => release_issue_labels,
    :milestone => milestone.number
    )
  puts "Created issue \##{issue.number} '#{release_description}'."

  puts "Creating release '#{args.milestone_version}'..."
  client.create_release(
    repo,
    args.milestone_version,
    :name => args.milestone_version,
    :draft => true,
    :body => release_body
    )
  puts "Created release '#{args.milestone_version}'."
end
{% endhighlight %}

Fairly straightforward, 

{% highlight ruby %}
repo = 'FakeItEasy/FakeItEasy'
release_issue_labels = ['0 - Backlog', 'P2', 'build', 'documentation']
release_issue_body = <<-eos
**Ready** when all other issues forming part of the release are **Done**.

- [ ] run code analysis in VS in *Release* mode and address violations (send a regular PR which must be merged before continuing)
- [ ] check build, update draft release in [GitHub UI](https://github.com/FakeItEasy/FakeItEasy/releases)
       including release notes, mentioning non-owner contributors, if any
- [ ] push NuGet package
- [ ] copy release notes from GitHub to NuGet
- [ ] de-list pre-release NuGet packages if present
- [ ] update website with contributors list (if in place)
- [ ] tweet, mentioning contributors and post link as comment here for easy retweeting ;-)
- [ ] post tweet in JabbR ([fakeiteasy][1] and [general-chat][2]) and Gitter ([FakeItEasy/FakeItEasy][3])
- [ ] post links to the NuGet and GitHub release in each issue in this milestone, with thanks to contributors
- [ ] use `rake set_version[new_version]` to change CommonAssemblyInfo.cs to expected minor version (of form _xx.yy.zz_)
- [ ] push to origin branch, create PR to upstream master
- [ ] use `rake create_milestone[new_version]` to
    - create a new milestone for the next release
    - create new issue (like this one) for the next release, adding it to the new milestone
    - create a new draft GitHub Release 
- [ ] close all issues on this milestone
- [ ] close this milestone

[1]: https://jabbr.net/#/rooms/fakeiteasy
[2]: https://jabbr.net/#/rooms/general-chat
[3]: https://gitter.im/FakeItEasy/FakeItEasy
eos

release_body = <<-eos
* **Changed**: _&lt;description&gt;_ - _#&lt;issue number&gt;_
* **New**: _&lt;description&gt;_ - _#&lt;issue number&gt;_
* **Fixed**: _&lt;description&gt;_ - _#&lt;issue number&gt;_

With special thanks for contributions to this release from:

* _&lt;user's actual name&gt;_ - _@&lt;github_userid&gt;_
eos
{% endhighlight %}


[checklists]: http://atulgawande.com/book/the-checklist-manifesto/
[githubapi]: https://developer.github.com/v3/