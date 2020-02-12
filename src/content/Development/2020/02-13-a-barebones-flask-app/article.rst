A Bare-bones Flask App
######################

:tags: flask, LibraryHippo, heroku
:series: LibraryHippo 2020

Last time I laid out the uncertainties that have to be explore before I want to
try hosting LibraryHippo on Heroku. Here they are again, roughly in descending
order of importance and risk:

1. web app hosting
2. scheduled jobs
3. scraping library websites on users' behalf
4. a small (perhaps a few MB) persistent datastore
5. authentication via social accounts
6. sending e-mail
7. free, or nearly so; as I said, this is a hobby project, and I'm not willing to dump several tens of dollars into it every month
8. job queues
9. custom domain name

Today I'll address the first of those: web app hosting. It's not particularly
risky, but it's very important. I'll start with an essentially empty repository:
just a license file, readme, and a :code:`.gitattributes` file.

Requirements
============

As I type, Heroku
`supports the Python 3.8.1 runtime <https://devcenter.heroku.com/changelog-items/1722>`_,
so I upgraded from 3.8.0 and then I created a virtual environment to work in,
upgraded pip, and installed Flask.

Typically Flask will read some some values, such as the application file,
secrets, or other configuration, from environment variables. I prefer to use
`python-dotenv <https://saurabh-kumar.com/python-dotenv/>`_ and to save them in
files (some committed, some not) for local use.

Finally, I install `Invoke <https://www.pyinvoke.org/>`_, since I can never
remember the syntax for the various tasks I have to do and tools I need to use
to them, and I think it's a nicer system than "a dozen batch files" that
accreted in the old LibraryHippo. Those should be all the dependencies I need
for now, so I freeze a ``requirements.txt`` file.

.. code:: powershell
    :class: m-console

    py -3.8 -m venv venv
    venv\Scripts\activate
    py -m pip install --upgrade pip
    pip install flask
    pip install python-dotenv
    pip install invoke
    pip freeze | Out-File -encoding ascii requirements.txt


Create a Flask application
==========================

Now I'm ready to create an application! We need three files:

.. code-figure:: app/__init__.py

    .. code:: python

        from flask import Flask

        app = Flask(__name__)

        from app import routes

.. code-figure:: app/routes.py

    .. code:: python

        from app import app

        @app.route("/")
        @app.route("/index")
        def index():
            return "LibraryHippo 2020"

.. code-figure:: libraryhippo.py

    .. code:: python

        from app import app

Typically, one would then set the ``FLASK_APP`` environment variable to
``libraryhippo.py``, but I find that inelegant, and I don't really enjoy making
sure it's set when I need it. Instead I'll set it in a ``.flaskenv.py`` file:

.. code-figure:: .flaskenv.py

    .. code:: shell

        FLASK_APP=libraryhippo.py

I'll create a ``run`` task in ``tasks.py`` so I remember how to run the
application, and then invoke it:

.. code-figure:: tasks.py

    .. code:: python

        from invoke import task

        @task
        def run(c):
            """Run local version of the application"""
            c.run("flask run")


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

And voilà:

.. figure:: {attach}local-libraryhippo.png
    :alt: screenshot of LibraryHippo running locally

    LibraryHippo running locally

It's not especially pretty, and it doesn't do a thing, but it's a running app.

Deploy to Heroku
================

Before deploying I needed

1. a Heroku account and
2. the Heroku :abbr:`CLI (command-line interface)`

I'd already signed up for a free account and installed the Heroku CLI while
going through
`The Flask Mega-Tutorial <https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world>`_,
so I can move right ahead with the work necessary for this application.


Create a Heroku Application
---------------------------

Heroku needs an application to associate with your code. Use the CLI to add an
application with a unique name:

.. console-figure::

    .. code :: powershell
        :class: m-console

        heroku apps:create libraryhippo

    .. code :: text
        :class: m-nopad

        Creating ⬢ libraryhippo... done
        https://libraryhippo.herokuapp.com/ | https://git.heroku.com/libraryhippo.git


Success! The last line of the output indicates the URL of the deployed
application (it's boring right now, since it doesn't have the LibraryHippo code)
and the URL of the git repository to push versions of LibraryHippo to.


Satisfy Heroku's Requirements
-----------------------------

Heroku needs a ``Procfile`` to understand how to run an application. So far
LibraryHippo's is simple:

.. code-figure:: Procfile

    .. code:: text

        web: gunicorn libraryhippo:app

This tells Heroku to use a web dyno to run the
`Gunicorn <https://gunicorn.org/>`_ web server, which will host the LibraryHippo
application. Gunicorn is required because the native Flask web server is not
production-ready.

Of course, a Heroku web dyno doesn't come with Gunicorn installed, so it needs
to be added to the requirements and frozen:

.. code:: powershell
    :class: m-console

    pip install gunicorn
    pip freeze | Out-File -encoding ascii requirements.txt

Finally, Heroku needs to know which version of Python to use. It has its own
defaults, but I prefer to know that my local environment is in sync with
Heroku's, so add a ``runtime.txt`` file to tell Heroku what I expect:

.. code-figure:: runtime.txt

    .. code:: text

        python-3.8.1

Push the code to Heroku
-----------------------

I'd been committing my code to a local git repository as I went, so
``heroku apps:create`` automatcially added a new remote called "heroku" for me;

.. console-figure::

    .. code:: powershell
        :class: m-console

        git remote -v

    .. code:: text
        :class: m-nopad

        heroku  https://git.heroku.com/libraryhippo.git (fetch)
        heroku  https://git.heroku.com/libraryhippo.git (push)
        origin  git@github.com:blairconrad/LibraryHippo.git (fetch)
        origin  git@github.com:blairconrad/LibraryHippo.git (push)

If I hadn't had git set up already, I could do so now and add the remote
manually.

Pushing to Heroku was to have been anticlimactic, but I kept messing up the
syntax of the git command. Heroku serves apps from the ``master`` branch, and
I'm working in ``lh2020``. The command that I thought meant "push lh2020 to
heroku as master" actually just pushed lh2020 *and* master, but the latter has
the code for the existing application, not the new Flask one. To save myself
from making this mistake again, I added a task:

.. code-figure:: tasks.py

    .. code:: python

        …

        @task
        def deploy(c):
            """Deploy the application to Heroku"""
            c.run("git push heroku lh2020:master")

And now the new LibraryHippo is running on Heroku.

.. figure:: {attach}heroku-libraryhippo.png
    :alt: screenshot of LibraryHippo running on Heroku

    LibraryHippo running on Heroku