Why I Teach Git Using Only the Command Line
###########################################

:tags: git

At the Day Job, we're about to transition something like 150 Subversion repos to
a single git monorepo. Part of my contribution will be training several tens of
git-unaware developers in my office on the basics of working with git.

I was chatting about training approaches with my counterpart in another office
(which already has a higher level of git experience) and he mentioned that his
local colleagues are committed (sorry) to using Tortoise SVN and similar tools,
and he wondered how I was going to handle GUI vs. CLI training.

I figured I'd have to address that question a few times in the coming weeks, so
I decided to write it down here.

All Command Line
================

As the title of this article hints, the answer to my colleague's question is
that I plan on handling GUI training by not doing any at all. I anticipate this
will be less than popular with my trainees, many of whom I know love their File
Explorer extensions for interfacing with Subversion. However, I have three
reasons for potentially disappointing them.

Too many GUIs to choose from
----------------------------
First, if I did use a GUI tool to train the users, which one? Off the top of my
head, I can think of `TortoiseGit <https://tortoisegit.org/>`_,
`SourceTree <https://www.sourcetreeapp.com/>`_,
`GitKraken <https://www.gitkraken.com/>`_, `fork <https://git-fork.com/>`_, and
systems embedded into the three popular editors in the office: Visual Studio
Code, Eclipse, and IntelliJ. The time required to develop and execute a plan for
even half of these is prohibitive, and picking just one isn't going to
appease near everyone.


Lack of tool knowledge
----------------------
Even if I did choose one or two GUI tools to focus on, hoping that I'd cover an
overlapping subset that would make most people happy, I'd have to learn how to
use the tools. It's been quite a while since I used a GUI tool (I enjoyed
GitKraken for a while, mostly because it's so pretty), and I'd need at least a
refresher, and potentially to completely retrain myself. I've never touched the
source control integration in Visual Studio Code, for example, despite using
that editor *right now*, with an intent to add this file to git.

GUIs lack transparency
----------------------

Finally, I've seen people use GUI git tools when they get started working with
git. I watched me do it. I don't think it helps. Having a pretty graphical view
of the commits is enjoyable, and being able to pick a few popular actions from a
menu helps the novice accomplish simple tasks, but after that the GUI becomes a
barrier to learning.

A number of the GUI tools handle housekeeping tasks, such as fetching from
remotes, for users. Or they perform so many background operations per explicit
action that the user takes, that they introduce confusion. I've several times
been called to my (smaller, informally introduced to git) team members' desks
and been asked what happened to their commit graph. Poring over the
incomprehensible snarl, I ask "what did you do?". They either point at some
confusingly-named action in a menu or say they picked some option from the menu,
they don't remember which.

By having developers actually type commands to fetch updates, switch branches,
commit, and rebase (and to constantly ``git log --graph --decorate --all`` after
each repository-modifying command), I'm hoping it will force them to think about
their actions and to develop a sense of how the git graphs change. Ideally they
will know what commands to execute to perform a particular task, or be able to
determine compensating actions to repair mistakes.

Or if things go horribly wrong, at least I'll be able to have them scroll up
through their command history to answer "what did you *do*?".
