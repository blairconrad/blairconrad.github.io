LibraryHippo 2020 - Running Scheduled Tasks on Heroku
#####################################################

:tags: LibraryHippo, flask, heroku, cron
:series: LibraryHippo 2020

Having established that a Flask app running on Heroku can send e-mail, I turn my
attention to having LibraryHippo do so periodically. The approach will be to
change the e-mail-sending to be something that can more easily be triggered from
the outside, and then triggering it from from time to time.

Making a Custom Flask command
=============================

On Google App Engine, every action had to be run via the web interface, so they
had to be secured by special credentials, which `could be a little tricky
<{filename}../../2015/01-05-app-engine-external-authentication-exposing-handlers-to-cron.md>`_.
Being able to write the tasks essentially as scripts under Flask/Heroku removes
a lot of complexity. These scripts are what Flask calls
`custom commands <https://flask.palletsprojects.com/en/1.1.x/cli/#custom-commands>`_;
they can be invoked from outside the web application, but with all the context
(such as the e-mail configuration set up last time) of the the full application.

First, I created new ``app/cli.py`` file to hold the command:

.. code-figure:: app/cli.py

    .. code:: python

        import time

        from app import mail
        from datetime import datetime
        from flask_mail import Message


        def register(app):
            @app.cli.command("notify-all")
            def notify_all():
                now = datetime.now().isoformat()

                msg = Message(
                    "LibraryHippo starting notifications", recipients=["blair@blairconrad.com"]
                )
                msg.body = f"starting notifications at {now}"
                msg.html = f"<h1>Test mail from LibraryHippo</h1><p>{msg.body}."

                print(msg.body)
                mail.send(msg)

                time.sleep(300)

                now = datetime.now().isoformat()

                msg = Message(
                    "LibraryHippo ending notifications", recipients=["blair@blairconrad.com"]
                )
                msg.body = f"ending notifications at {now}"
                msg.html = f"<h1>Test mail from LibraryHippo</h1><p>{msg.body}."

                print(msg.body)
                mail.send(msg)

This was taken from the old ``sendmail`` web route, which I removed completely, and then updated to

1. send two e-mails, just to make sure we could, and
2. sleep for 5 minutes between e-mails, to verify that Heroku won't kill a longer-running task

I called the task ``notify-all``, since I'm simulating that action in the
existing LibaryHippo: notifying all families of their library card status. The
command can be invoked by running

.. code:: powershell
    :class: m-console

    flask notify-all

and it performs exactly how you'd hope.

Once the new version of the application is deployed using ``inv deploy``, it's
even possible to run the task *on a Heroku dyno* via

.. console-figure::

    .. code:: powershell
        :class: m-console

        heroku run flask notify-all


    .. code:: text
        :class: m-nopad

        Running flask notify-all on ⬢ libraryhippo... up, run.2562 (Free)
        starting notifications at 2020-02-10T11:56:25.840194
        ending notifications at 2020-02-10T12:01:26.234036

Scheduling the Task
===================

There are a number of options for scheduling repeated tasks on Heroku, but a
very simple (and free!) one is the
`Heroku Scheduler <https://devcenter.heroku.com/articles/scheduler>`_ add-on. It
hasn't the flexibility of other schedulers, supporting only daily, hourly, or
10-minutely schedules. Still, LibraryHippo just needs to send e-mails once per
day and check users' cards about that often, so it should do.

Adding the scheduler is very easy:

.. console-figure::

    .. code:: powershell
        :class: m-console

        heroku addons:create scheduler:standard

    .. code:: text
        :class: m-nopad

        Creating scheduler:standard on ⬢ libraryhippo... free
        To manage scheduled jobs run:
        heroku addons:open scheduler

        Created scheduler-curved-17868
        Use heroku addons:docs scheduler to view documentation

A short search didn't reveal a way to affect the schedule from the console, but
it was easy enough to open the web-based configuration.

.. console-figure::

    .. code:: powershell
        :class: m-console

        heroku addons:open scheduler

    .. image:: {attach}empty-scheduler-config.png
        :alt: Screenshot of empty Heroku Scheduler configuration page

Adding a job is as simple as choosing "Create job", selecting a time to run, and
typing the command to execute, which in this case was ``flask notify-all``.
I chose to execute daily at 11:30 PM because as I typed, it was 11:26 PM UTC.

.. figure:: {attach}configure-job-for-2330.png
    :alt: Screenshot of configuring a job to run daily at 11:30 PM

    Configuring a job to run daily at 11:30 PM

Now there's nothing to do but wait. In the meantime I opened up the LibraryHippo
application's log view (at https://dashboard.heroku.com/apps/libraryhippo/logs)
and watched.

Shortly after 6:30 PM local time, the log started updating, and I received my
first e-mail, with further updates and a second e-mail about 5 minutes later.
The log looked like this:

.. figure:: {attach}heroku-log.png
    :alt: Screenshot of Heroku log of scheduled e-mail task run

    Heroku log of scheduled e-mail task run

Note that there are some earlier entries from the manually-invoked test run I'd
done at 2020-02-10T12:01:29, and also from the web worker that had been active
from some earlier time and was shut down due to inactivity at 12:26:17.

At 23:30:25, the ``flask notify-all`` worker starts up, running achieving an
"up" state before logging (via the ``print`` statements in the code) the two
e-mail messages that it sent, and finally transitioning to a "complete" state
and shutting down at 23:35:28.

And the e-mails arrived right on schedule:

.. figure:: {attach}e-mails-sent-from-scheduled-job.png
    :alt: Screenshot of scheduled e-mails
    
    Scheduled e-mails arriving over 5 minutes

A Note on Time Zones
====================

As the documentation states, Heroku Scheduler jobs use a clock in the
`UTC time zone <https://en.wikipedia.org/wiki/Coordinated_Universal_Time>`_, but
LibrayHippo's customers live in the
`Eastern Time Zone <https://en.wikipedia.org/wiki/Eastern_Time_Zone>`_ (of the
Americas), which is either 5 or 4 hours behind UTC, depending on whether
daylight saving time is in effect. When I ran my test, I wanted the e-mails to
be sent near 18:30 in my local time zone, and daylight saving time was not in
effect, so I scheduled the job for 23:30 UTC.

Configuring the jobs with an offset is not particularly onerous, but it does
mean that once daylight saving time takes effect, users will see their e-mails
start arriving an hour later in the day. This is annoying, but can be worked
around in a variety of ways. I'll probably just configure the notification job
to run at 10:00 UTC, so e-mails arrive near 5:00 local time in the winter and
6:00 in the summer.

Some alternatives to having the e-mail delivery time shift with the seasons are
to pay for a more expensive and sophisticated scheduler, or to further
workaround by having 2 scheduled jobs. One could run at 10:00 UTC and one at
11:00 UTC. They could each check whether daylight saving time were active in the
Eastern Time Zone, ensuring that only the proper job ran. But I'll leave that
for later. Or never.

Progress
========

Three of nine requirements have been met.

.. csv-table::
    :class: m-table

    :label-success:`done`, web app hosting,
    :label-success:`done`, scheduled jobs, "run in UTC, requiring job start times be offset from local time"
    :label-primary:`next`, scraping library websites on users' behalf,
       , small persistent datastore,
       , social authentication,
    :label-success:`done`, sending e-mail,
       , nearly free,
       , job queues,
       , custom domain name,

