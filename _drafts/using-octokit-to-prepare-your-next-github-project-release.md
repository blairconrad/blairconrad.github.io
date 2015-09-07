---
layout: post
title: "Using Octokit to Prepare Your Next GitHub Project Release"
comments: true
tags: 
      - releasing
      - octokit
      - ruby
---

At the Day Job, I work on a rather large enterprise application whose
minor releases come out about twice a year, and larger releases
considerably less frequently.  As such, it was very refreshing to jump
on board the [FakeItEasy](http://fakeiteasy.github.io/) team, where
frequent small releases are de rigueur.

One problem having frequent small releases is that you
frequently have to release. The act of releasing

* steals time from other activities that could provide value, and
* is an opportunity to foul up and generate a flawed release

Of course, not releasing isn't a viable option, so we have to accept
some loss of time and some risk of introducing errors, but we can try
to minimize both.

One way to improve productivity and increase consistency is to use
[checklists][checklists].  When I showed up at FakeItEasy Enterprises,
each new release was described by an issue that included a
comprehensive checklist, such as this one:

<figure>
  <a href="https://github.com/FakeItEasy/FakeItEasy/issues/272"><img src="{{ site.image_dir }}/release_checklist.png"></a>
</figure>

I found this extremely helpful as I made my first releases. The main
benefit was that the list of steps ensured that I didn't forget
anything.  However, the list was fairly long, at 15 steps, in spite of
efforts to streamline the process. So more recently I find myself
chafing at repeating some tasks.

While it would be nice to just push a button and have the release
done, there will always be some manual work&mdash;I wouldn't trust a
robot to generate a tweet that correctly thanked contributors, for
example. Still, I went looking for some steps that can be
streamlined.

For my first task, I focused on creating the next GitHub release,
milestone, and release issue. These tasks don't really require any
intelligence, other than picking the next release number, and all can
be accomplished using the [GitHub API][githubapi]. Another benefit of
grouping these activities in a Rake task is that creating the next
GitHub release while closing the current one means the next release
draft can be edited as contributing issues are marked as done,
ensuring that release notes and thank-yous are accurate.

The Rake task is called `create_milestone` and is fairly simple:

<pre><code>desc "create new milestone, release issue and release"
task :create_milestone do |t|
  require 'octokit'

  ssl_cert_file = get_temp_ssl_cert_file(ssl_cert_file_url)

  client = Octokit::Client.new(:netrc => true)

  release_description = version + ' release'

  puts "Creating milestone '#{version}'..."
  milestone = client.create_milestone(
    repo,
    version,
    :description => release_description
    )
  puts "Created milestone '#{version}'."

  puts "Creating issue '#{release_description}'..."
  issue = client.create_issue(
    repo,
    release_description,
    release_issue_body,
    :labels => release_issue_labels,
    :milestone => milestone.number
    )
  puts "Created issue \##{issue.number} '#{release_description}'."

  puts "Creating release '#{version}'..."
  client.create_release(
    repo,
    version,
    :name => version,
    :draft => true,
    :body => release_body
    )
  puts "Created release '#{version}'."
end
</code></pre>

As you can see, the task creates

- a milestone with the same name as the upcoming version,
- a "build/release" issue to put in that milestone, and
- a draft release likewise named after the next version of the product.

(The `get_temp_ssl_cert_file` business just downloads a temporary SSL
certificate to work around a SSL_connect Error With Ruby on
Windows. If you're interested, you can read all about it in the
[FakeItEasy rakefile][rakefile].)

The `version` variable is read from the `CommonAssemblyInfo.cs`
file. The other relevant variables are defined in the rakefile, and of
course would vary by project, but here's what we're using today:

<pre><code>repo = 'FakeItEasy/FakeItEasy'
release_issue_labels = ['0 - Backlog', 'P2', 'build', 'documentation']
release_issue_body = <<-eos
**Ready** when all other issues forming part of the release are **Done**.

- [ ] run code analysis in VS in *Release* mode and address violations (send a regular PR which must be merged before continuing)
- [ ] if necessary, change `VERSION_SUFFIX` on [CI Server](http://teamcity.codebetter.com/admin/editBuildParams.html?id=buildType:bt929)
      to appropriate "-beta123" or "" (for non-betas) value and initiate a build
- [ ] check build
-  edit draft release in [GitHub UI](https://github.com/FakeItEasy/FakeItEasy/releases):
    - [ ] complete release notes, mentioning non-owner contributors, if any
    - [ ] attach nupkg
    - [ ] publish the release
- [ ] push NuGet package
- [ ] copy release notes from GitHub to NuGet
- [ ] de-list pre-release or superseded buggy NuGet packages if present (copy any release notes forward to the new version)
- [ ] update website with contributors list (if in place)
- [ ] tweet, mentioning contributors and post link as comment here for easy retweeting ;-)
- [ ] post tweet in JabbR ([fakeiteasy][1] and [general-chat][2]) and Gitter ([FakeItEasy/FakeItEasy][3])
- [ ] post links to the NuGet and GitHub release in each issue in this milestone, with thanks to contributors
- [ ] use `rake set_version[new_version]` to 
    - create a new branch
    - change CommonAssemblyInfo.cs to expected minor version (of form _xx.yy.zz_)
    - push to origin
    - create PR to upstream master
- [ ] use `rake create_milestone` to
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
eos</code></pre>

The task's been a big help to me over the last few months, along with a companion task, `set_version`, which branches, updates the version number in `CommonAssemblyInfo.cs` and submits a pull request to GitHub:

<pre><code>desc "Update version number"
task :set_version, :new_version do |asm, args|
  current_branch = `git rev-parse --abbrev-ref HEAD`.strip()
  
  if current_branch != 'master'
    fail("ERROR: Current branch is '#{current_branch}'. Must be on branch 'master' to set new version.")
  end if

  new_version = args.new_version
  new_branch = "set-version-to-" + new_version

  require 'octokit'

  ssl_cert_file = get_temp_ssl_cert_file(ssl_cert_file_url)

  client = Octokit::Client.new(:netrc => true)

  puts "Creating branch '#{new_branch}'..."
  `git checkout -b #{new_branch}`
  puts "Created branch '#{new_branch}'."

  puts "Setting version to '#{new_version}' in '#{assembly_info}'..."
  Rake::Task["set_version_in_assemblyinfo"].invoke(new_version)
  puts "Set version to '#{new_version}' in '#{assembly_info}'."

  puts "Committing '#{assembly_info}'..."
  `git commit -m "setting version to #{new_version}" #{assembly_info}`
  puts "Committed '#{assembly_info}'."

  puts "Pushing '#{new_branch}' to origin..."
  `git push origin #{new_branch}"`
  puts "Pushed '#{new_branch}' to origin."

  puts "Creating pull request..."
  pull_request = client.create_pull_request(
    repo,
    "master",
    "#{client::user.login}:#{new_branch}",
    "set version to #{new_version} for next release",
    "preparing for #{new_version}"
  )
  puts "Created pull request \##{pull_request.number} '#{pull_request.title}'."
end</code></pre>

(`set_version_in_assemblyinfo` is a task that uses
[Albacore][albacore] to write the new version number in the file. If
you're interested, read more in the [FakeItEasy rakefile][rakefile].)

[checklists]: http://atulgawande.com/book/the-checklist-manifesto/
[githubapi]: https://developer.github.com/v3/
[rakefile]: https://github.com/FakeItEasy/FakeItEasy/blob/21a386b3f85cda7220e130ec554c5a547209b4b5/rakefile.rb
[albacore]: http://albacorebuild.net/
