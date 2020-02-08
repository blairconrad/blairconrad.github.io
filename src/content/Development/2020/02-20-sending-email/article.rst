Sending Email from Heroku
#########################

:tags: LibraryHippo, flask, heroku, email
:series: LibraryHippo 2020

After getting a do-nothing web app running on Heroku, I think the riskiest
requirement is having a scheduled job for LibraryHippo to check families' status
and notify them. However rather than trying to satisfy that requirement, this
time I'm going to try to set up email sending, mostly because it can be used as
the triggered action, making it easier to test the scheduled jobs.


Requirements
============

Flask has a plugin to make sending mail easier,
`Flask-Mail <https://pythonhosted.org/Flask-Mail/>`_; I'll install it, but first
I'll add a task to freeze the ``requirements.txt`` file, since I'm tired of
using the Powershell syntax to do that.

.. code-figure:: tasks.py

    .. code:: python

        @task
        def freeze(c):
            """Freeze pip's requirements.txt. Does not commit the file."""
            import pip

            result = c.run("pip freeze")
            with open("requirements.txt", mode="w") as requirements:
                requirements.write(result.stdout)

Now to install the package:

.. console-figure::

    .. code:: powershell
        :class: m-console
    
        pip install Flask-Mail
        inv freeze

    .. code:: text
        :class: m-nopad

        Collecting Flask-Mail
        Using cached Flask-Mail-0.9.1.tar.gz (45 kB)
        Requirement already satisfied: Flask in d:\sandbox\libraryhippo\venv\lib\site-packages (from Flask-Mail) (1.1.1)
        Collecting blinker
        Using cached blinker-1.4.tar.gz (111 kB)
        Requirement already satisfied: itsdangerous>=0.24 in d:\sandbox\libraryhippo\venv\lib\site-packages (from Flask->Flask-Mail) (1.1.0)
        Requirement already satisfied: Werkzeug>=0.15 in d:\sandbox\libraryhippo\venv\lib\site-packages (from Flask->Flask-Mail) (0.16.1)
        Requirement already satisfied: Jinja2>=2.10.1 in d:\sandbox\libraryhippo\venv\lib\site-packages (from Flask->Flask-Mail) (2.11.1)
        Requirement already satisfied: click>=5.1 in d:\sandbox\libraryhippo\venv\lib\site-packages (from Flask->Flask-Mail) (7.0)
        Requirement already satisfied: MarkupSafe>=0.23 in d:\sandbox\libraryhippo\venv\lib\site-packages (from Jinja2>=2.10.1->Flask->Flask-Mail) (1.1.1)
        Installing collected packages: blinker, Flask-Mail
            Running setup.py install for blinker ... done
            Running setup.py install for Flask-Mail ... done
        Successfully installed Flask-Mail-0.9.1 blinker-1.4

        blinker==1.4
        Click==7.0
        Flask==1.1.1
        Flask-Mail==0.9.1
        gunicorn==20.0.4
        invoke==1.4.1
        itsdangerous==1.1.0
        Jinja2==2.11.1
        MarkupSafe==1.1.1
        python-dotenv==0.10.5
        Werkzeug==0.16.1


Flask-Mail Configuration
========================

The production LibraryHippo application uses `Sendgrid <https://sendgrid.com/>`_
as an email server, and I see no reason to deviate now. Flask-Mail must be
configured to use this server. Some of the configuration should remain a secret
(the password), and some *could* be hard-coded right in the app, but I prefer to
separate the configuration from the code. I'll put the public settings in a file
called ``configuration``, which will be committed, and the sensitive ones in
``secrets``, which I won't commit.

.. code-figure:: configuration

    .. code:: python
   
        MAIL_DEFAULT_SENDER=librarianhippo@gmail.com
        MAIL_PORT=587
        MAIL_SERVER=smtp.sendgrid.net
        MAIL_USE_TLS=True
        MAIL_USERNAME=apikey

.. code-figure:: secrets

    .. code:: python

        # Do not commit this file. It must not be shared.
   
        MAIL_PASSWORD=AN_API_KEY_THAT_I_WONT_SHARE_WITH_YOU


Code
====

Now to make Flask aware of the configuration from above and to add Flask-Mail to
the application so it can send email.

The ``Config`` class is a bridge that gives Flask access to the environment variables. It

1. provides a central location to view all configuration settings
2. supplies sensible defaults for settings that might have some, and
3. converts some settings from strings to their proper types, simplifying usage
   in the code.

.. code-figure:: config.py

    .. code:: python

        import os
        from dotenv import load_dotenv

        basedir = os.path.abspath(os.path.dirname(__file__))
        load_dotenv(os.path.join(basedir, "secrets"))
        load_dotenv(os.path.join(basedir, "configuration"))


        class Config(object):
            MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER")
            MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
            MAIL_PORT = int(os.environ.get("MAIL_PORT") or 25)
            MAIL_SERVER = os.environ.get("MAIL_SERVER")
            MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS") != "False"
            MAIL_USERNAME = os.environ.get("MAIL_USERNAME")


Then 4 lines are added to the application initialization to hook the
configuration class and Flask-Mail into the application:

.. code-figure:: app/__init__.py

    .. code:: python
        :hl_lines: 1 4 7 9

        from config import Config

        from flask import Flask
        from flask_mail import Mail

        app = Flask(__name__)
        app.config.from_object(Config)

        mail = Mail(app)

        from app import routes

Finally, a new route is added to the application to trigger the email. Note that
this is completely unprotected and a horrible, horrible idea for a production
environment, as someone could just visit the page and spam me. But it makes for
an easy test.


.. code-figure:: routes.py

    .. code:: python

        from app import app
        from app import mail
        from datetime import datetime
        from flask_mail import Message

        @app.route("/sendmail")
        def sendmail():
            now = datetime.now().strftime("%c")
            msg = Message("Mail from LibraryHippo", recipients=["blair@blairconrad.com"])
            msg.body = f"test mail from LibraryHippo at {now}"
            msg.html = f"<h1>Test mail from LibraryHippo</h1><p>It's now {now}."
            mail.send(msg)
            return f"Sent mail at {now}"

And it works! I can trigger the route and get a success message. Nearly
instantaneously, I receive the email in my inbox.

.. console-figure::

    .. code:: powershell
        :class: m-console

        inv run

    .. code:: text
        :class: m-nopad

        * Serving Flask app "libraryhippo.py"
        * Environment: production
        WARNING: This is a development server. Do not use it in a production deployment.
        Use a production WSGI server instead.
        * Debug mode: off
        * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
        127.0.0.1 - - [07/Feb/2020 06:08:38] "GET /sendmail HTTP/1.1" 200 -


.. figure:: {attach}local-sendmail.png
    :alt: screenshot of LibraryHippo having sent mail locally

    LibraryHippo having sent mail locally


.. figure:: {attach}local-received-mail.png
    :alt: screenshot of email received from local LibraryHippo

    Email received from local LibraryHippo

Deploying to Heroku
===================

There's very little work to do to deploy to Heroku. All the new configuration
settings are in the ``configuration`` file except for ``MAIL_PASSWORD``. The
Heroku web interface provides a way to set the value, but it's easier to use the
Heroku command line interface:

.. console-figure::

    .. code:: powershell
        :class: m-console

        heroku config:set "MAIL_PASSWORD=AN_API_KEY_THAT_I_WONT_SHARE_WITH_YOU"

    .. code:: text
        :class: m-nopad

        Setting MAIL_PASSWORD and restarting ⬢ libraryhippo... done, v4
        MAIL_PASSWORD: AN_API_KEY_THAT_I_WONT_SHARE_WITH_YOU

And now to deploy and test

.. console-figure::

    .. code:: powershell
        :class: m-console

        inv deploy

    .. code:: text
        :class: m-nopad

        remote: Compressing source files... done.
        remote: Building source:
        remote:
        remote: -----> Python app detected
        remote: -----> Need to update SQLite3, clearing cache
        remote: -----> Installing python-3.8.1
        remote: -----> Installing pip
        remote: -----> Installing SQLite3
        remote: Sqlite3 successfully installed.
        remote: -----> Installing requirements with pip
        #
        # a lot of boring pip stuff
        #
        remote:        Successfully installed Click-7.0 Flask-1.1.1 Flask-Mail-0.9.1 Jinja2-2.11.1 MarkupSafe-1.1.1 Werkzeug-0.16.1 blinker-1.4 gunicorn-20.0.4 invoke-1.4.1 itsdangerous-1.1.0 python-dotenv-0.10.5
        remote:
        remote: -----> Discovering process types
        remote:        Procfile declares types -> web
        remote:
        remote: -----> Compressing...
        remote:        Done: 47.9M
        remote: -----> Launching...
        remote:        Released v5
        remote:        https://libraryhippo.herokuapp.com/ deployed to Heroku
        remote:
        remote: Verifying deploy... done.
        To https://git.heroku.com/libraryhippo.git
        3f0598d..ddf4728  lh2020 -> master

.. figure:: {attach}heroku-sendmail.png
    :alt: screenshot of LibraryHippo having sent mail from Heroku

    LibraryHippo having sent mail from Heroku


.. figure:: {attach}heroku-received-mail.png
    :alt: screenshot of email received from LibraryHippo on Heroku

    Email received from LibraryHippo on Heroku

Note the time discrepancy between the time that LibraryHippo reported and the
time that GMail said it receive the message. I'm sending from UTC-5, and the
Heroku server appears to be in UTC. It's not a problem for now, but may become a
factor when scheduling jobs.

Progress Report
===============

Two of eight requirements have been met.

.. csv-table::
    :class: m-table

    :label-success:`done`, web app hosting,
    :label-primary:`next`   , scheduled jobs,  :label-warning:`may only run in UTC`
       , small persistent datastore,
       , social authentication,
    :label-success:`done`, sending e-mail,
       , nearly free,
       , job queues,
       , custom domain name,

