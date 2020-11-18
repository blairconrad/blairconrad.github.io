How Untested Changes Block Merges to Master: a Guide for Non-Developers
#######################################################################

:tags: git

At the Day Job, I work on a product that over two dozen development teams
contribute to. To provide some level of stability on the branch that we release
from (called "master"), each team has their own development branch and we merge
from the team branches to the master branch only after

1. a suite of automated feature and regression tests pass, and
2. new features are manually tested

Ideally, the new features (or bugfixes) would be tested quickly and in the order
that they were added to the team branch, but this doesn't always happen. Some
issues take a very long time to test and the developers race ahead, and
sometimes issues fail. In these situations, some changes that have met the above
conditions must wait to be merged to the master branch.

Often non-developer teammates and servant leaders ask me *why* a tested issue is
blocked by an untested (or failed!) issue. This is my attempt to explain why.
Hopefully it's accessible to those without previous git knowledge.

Git: a Collection of Changes
============================

Git, like any version control system, exists to track the evolution of a body
information (often a codebase). It does so by keeping track of changes that
happen over time. Each change (or "commit" as they are called in git) can
include one or more file additions, deletions, or modifications. Once commits
are added to the master or team branch, they cannot be removed or changed;
they're permanent.

Here's a very simple representation of a collection of git commits. Letters
represent individual commits, and the arrows indicate pointers from commits to
the preceding commit (or "parent")::

    A <-- B <-- C <-- D

In this diagram, time moves to the right, so A was the first change, B next (and
it knows about its parent A), and so on, to the most recent commit, D.

Sometimes the arrowheads can clutter the graph, so I'll omit them in subsequent
diagrams. In all cases, time will move the right, so to figure out the full
state of a branch, you start at the right-hand side and follow the lines to the
left. Given this convention, the above diagram would look like this::

    A --- B --- C --- D

Merging between branches
========================

Let's add a second branch and label them, to model the system I deal with at
work

.. include:: master-and-team-branch.ansi
    :code: ansi

Here we see the master branch with commits P, Q, R, and S (the latest) and the
team branch with A, B, C, and D. Each of the commits I mentioned exist only in
their own branch. In particular, this means that the commits in the team branch
will not be built into our product and make it to our customers, since we build
and ship from the master branch.

We incorporate the team-level changes in the team branch via a git "merge",
which sounds very fancy, but it's just another commit. A merge commit melds
divergent histories by having two parents. Once the merge commit is added to a
branch any commits that are reachable by following the links from that commit
back to the left are "part of" the branch:

.. include:: merge-team-into-master.ansi
    :code: ansi

Here we've merged the team branch into the master branch by creating a new merge
commit called T on the master branch. Now all of the work we've done on the
master branch and on the team branch has been consolidated into the master
branch, so the next time we build the product, we'll get all the benefits.

You don't always have to merge the last commit of a branch into another branch.
Suppose we had some bonus commits on the team branch that we just didn't want to
merge into the master branch yet for whatever reason. We could do this:

.. include:: merge-past-team-into-master.ansi
    :code: ansi

Then

* A, B, C, D, P, Q, R, S, and T are all part of the master branch, and
* A, B, C, D, E, and F are part of the team branch, but
* E and F are not (yet) part of the master branch.

Even though we can pick essentially any commit to merge into the master branch,
what we can't do is omit that commit's ancestors. If we merge a commit D as
above, we always take C, B, and A, because we can reach those commits by
following the parent links to the left from D.

Blocking commits
================

Up till now we've not really been looking at the worthiness of particular
commits when deciding what to merge. Suppose

#. we have 4 commits in master and 4 in the team branch
#. the team branch passed all automated tests,
#. the issues addressed by the first, second, and fourth team commits have been manually tested
#. but the issue addressed by the third team commit has not yet been tested.

We'll represent the commits that has not yet been manually tested with a
lowercase letter to show that it's not "done":

.. include:: untested-commit.ansi
    :code: ansi

Under our rules, A, B, and D are considered complete and worthy of merging, but
c is not. Maybe it's fine, but we don't know yet, and we promised not to merge c
into the master branch until it's known to be good.

There's no way to merge D into the master branch given our rules. We could merge
A and B like so:

.. include:: merge-just-before-untested-commit.ansi
    :code: ansi

(or similarly just A). But if we want to merge D in, we'd end up getting c, B,
and A as well. It would look like this:

.. include:: merge-including-untested-commit.ansi
    :code: ansi

And that violates our rules: c has not yet met all its merging conditions, but
it's been merged into the master branch. We can start at the latest commit in
the master branch (T) and follow the lower parent link to the left (and down) to
D, and then follow its link to c. We've risked polluting the master branch with
an unproven change.

How to Unblock the Branch
=========================

Ultimately we want to merge all of our proven work from the team branch into the
master branch. How do we do that?

Focus on the blocking commit and wait
-------------------------------------

This is the approach we take most often. The commit called c hasn't been tested
above, but it will be sometime. When we notice that we have blocked commits, as
a team we can concentrate on completing the testing for the blocking commits.
Once they are found to be good, they're no longer blockers and we can merge them
or any other subsequent commits, so long as all of those have been found worthy.
This is the strategy we take most often.

Revert the offending commit
---------------------------

If the blocking commit is expected to take a very long time to test, we can
"revert" it. This is different from removing the commit (remember, once a commit
is added to a branch, you can't remove it). Reverting involves adding *another*
commit to the branch. The new commit undoes the original change. Here's what that
looks like:

.. include:: revert-offending-commit.ansi
    :code: ansi

Here "!c" represents a sort of anti-c that has the opposite of the changes
contained in c.

Once this is done, it's as if the team branch has only A, B, and D in it. But
there are some caveats:

* crafting and adding !c takes some development time, and time to run the
  automated tests to ensure that the team branch is still in good shape

* sometimes the commits between c and !c will build upon work in c. This means
  that

  * !c is harder to make, and

  * making !c runs the risk of compromising the work done in D (or other
    intervening commits—there could be more than one). Depending on the
    entanglement, it may even be necessary to manually retest the issue
    addressed by D

  * eventually we'll need to redo the work for c and test it then, perhaps
    running into the same problem we had this time

If we decide that reverting and merging are still worth it given all those
caveats, eventually we'll end up with

.. include:: merge-reverted-commit.ansi
    :code: ansi

While this approach is possible, it has significant downsides, and so we are
loath to use it when "focus and wait" is a viable option.

How to Avoid the Problem
========================

The problem of blocking commits is generally caused by a mismatch in the time it
takes for us to develop a change and that taken to test it. Our product's build
times and even automated testing times are quite long, so we'll naturally have
some mismatch, even if someone is available to perform manual testing
immediately after the change is in a team branch build. But there are ways to
reduce this gap or mitigate its effects. The ideas presented below are neither
comprehensive nor independent. In the coming months we could pursue more than
one of them, or think of something else.

More (reliable) automated testing
---------------------------------

Our ratio of automated to manual testing isn't great. Some portions of the
product have good automated tests and we have high confidence in them, but more
areas have lower coverage and therefore confidence. If developers and testers
were better at working together to establish what kinds of automated tests
should be written in conjunction with a bugfix or new feature, and if those
tests reliably produced consistent results, this might

1. slow down development
2. considerably shorten the manual testing phase
3. increase the likelihood that any manual testing phase will pass
4. provide lasting value in the form of automatically-run regression tests

Better planning and coordination
--------------------------------

Sometimes developers and testers fail to talk before an issue is developed, so
the change is added to the team branch when no testers are ready to test it, and
it languishes. Maybe certain issues require special hardware or complex
configuration, so the tester prefers to test B and D consecutively, deferring c
for a while, but the developer was unaware (or just didn't consider it).

If there were more and better intra-team planning, a change could be developed
just in time for it to be manually tested, reducing the time it sits in the team
branch, waiting for other issues to be cleared.

Manual testing before the team branch
-------------------------------------

I didn't discuss topic branches above, but they are a third type of branch where
developers do their low-level work. They feed into the team branches. In theory,
we could build packages from those branches and do the manual testing on them.
Then once the issue has passed, the topic branch's contents could be added to
the team branch. We'd only be waiting for the automated tests to run to clear
the branch, and this is generally quicker than manual testing (and can be done
overnight).

The downside to this approach is that it requires heavier weight automated
processes to be run on the topic branches (of which there are more than team
branches) and we're already resource-constrained. In addition, it means staging
more clusters for the manual testers to work on, again requiring more hardware
and time.
