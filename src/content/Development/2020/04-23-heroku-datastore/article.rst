LibraryHippo 2020 - A Small Heroku Datastore
############################################

:tags: LibraryHippo, flask, heroku, database
:series: LibraryHippo 2020
:summary:
    Now the Heroku-hosted LibraryHippo can perform periodic tasks, send e-mails, and
    scrape the Waterloo Public Library's website. All it needs is a datastore to tie
    these concepts together into a decoupled "push card status to patrons" pipeline.

Now the Heroku-hosted LibraryHippo can perform periodic tasks, send e-mails, and
scrape the Waterloo Public Library's website. All it needs is a datastore to tie
these concepts together into a decoupled "push card status to patrons" pipeline.

Move rendering out of library
=============================

Last time, the ``WPL.check_card`` method scraped a patron's holds and checkouts,
and rendered them as HTML for display to the user. It would be better to have
the library build a data structure, which can be stored for later use or
rendered by the web app.

.. code-figure:: app/libraries/wpl.py

    .. code:: python

        def check_card(self, patron, number, pin):
            session = Session()
            summary_page = self.login(session, patron, number, pin)

            holds_url = urllib.parse.urljoin(
                self.login_url(),
                summary_page.find(name="a", href=re.compile("/holds$"))["href"],
            )
            checkouts_url = urllib.parse.urljoin(
                self.login_url(),
                summary_page.find(name="a", href=re.compile("/items$"))["href"],
            )

            holds = self.get_holds(session, holds_url)
            checkouts = self.get_checkouts(session, checkouts_url)

            return {
                "holds": holds,
                "checkouts": checkouts,
            }

"Data structure" is maybe too fancy a term for "dictionary with two values", but
it's a start.

.. code-figure:: app/routes.py

    .. code:: python

        @app.route("/check")
        def check():
            card_check_result = WPL().check_card(
                Config.PATRON_NAME, Config.CARD_NUMBER, Config.PIN
            )

            result = "<h1>Holds</h1>"
            for hold in card_check_result["holds"]:
                result += "<dl>"
                for k, v in hold.items():
                    result += f"<dt>{k}</dt><dd>{v}</dd>"
                result += "</dl><hr>"

            result += "<h1>Checkouts</h1>"
            for checkout in card_check_result["checkouts"]:
                result += "<dl>"
                for k, v in checkout.items():
                    result += f"<dt>{k}</dt><dd>{v}</dd>"
                result += "</dl><hr>"

            return result

Create a local database
=======================

Flask doesn't come with a database of its own, like some web frameworks, but
there's an extension,
`Flask-SQLAlchemy <https://flask-sqlalchemy.palletsprojects.com/en/2.x/>`_, that
helps it work with the `SQLAlchemy <https://www.sqlalchemy.org/>`_ Object
Relational Mapper. These will let LibraryHippo interact with databases both
locally and on Heroku. It's good practice to track changes to the database
schema using `Flask-Migrate <https://github.com/miguelgrinberg/flask-migrate>`_,
so I'll install that as well.

.. code:: powershell
    :class: m-console

    pip install Flask-SQLAlchemy
    pip install Flask-Migrate
    inv freeze

Flask needs some configuration settings to access the database.
``SQLALCHEMY_DATABASE_URI`` describes how the application can contact the
database. In this case, there's a reasonable default, a local SQLite instance.
The ``SQLALCHEMY_TRACK_MODIFICATIONS`` setting will keep the database from
signalling the application whenever the database content changes.

.. code-figure:: config.py

    .. code:: python

        class Config(object):
            # …
            # Remove PATRON_NAME, CARD_NUMBER, and PIN, as they'll move to the database

            SQLALCHEMY_DATABASE_URI = os.environ.get(
                "DATABASE_URL"
            ) or "sqlite:///" + os.path.join(basedir, "app.db")
            SQLALCHEMY_TRACK_MODIFICATIONS = False

Then the application needs to be taught about the database and migration facilities:

.. code-figure:: app/__init__.py

    .. code:: python

        # …
        from flask_migrate import Migrate
        from flask_sqlalchemy import SQLAlchemy

        # …
        app = Flask(__name__)
        app.config.from_object(Config)

        mail = Mail(app)

        db = SQLAlchemy(app)
        migrate = Migrate(app, db)

        from app import routes, models

Add a Card
==========

The application now has the ability to talk to the database, but there's no
schema defined. Let's add a model and insert a record.

.. code-figure:: app/__init__.py

    .. code:: python

        class Card(db.Model):
            id = db.Column(db.Integer, primary_key=True)
            patron_name = db.Column(db.String(64))
            number = db.Column(db.String(32))
            pin = db.Column(db.String(16))
            last_state = db.Column(db.Text())

            def __repr__(self):
                return f"<Patron {self.patron_name}>"

Every model gets an ``id``, for convenience, and the next 3 fields will be
familiar from the previous article—they identify the card and control access to
the library card state. The last field, ``last_state``, will be used to record
the last-checked card state. It'll hold a JSON-formatted version of the
dictionary that appears above.

Initialize the database
-----------------------

Now initialize a schemaless database, add the first migration script for the
``Card`` model, and actually upgrade the database schema:

.. console-figure::

    .. code:: powershell
        :class: m-console
    
        flask db init
        flask db migrate -m "Add Card model"
        flask db upgrade

    .. code:: text
        :class: m-nopad

        Creating directory D:\Sandbox\LibraryHippo\migrations ...  done
        Creating directory D:\Sandbox\LibraryHippo\migrations\versions ...  done
        Generating D:\Sandbox\LibraryHippo\migrations\alembic.ini ...  done
        Generating D:\Sandbox\LibraryHippo\migrations\env.py ...  done
        Generating D:\Sandbox\LibraryHippo\migrations\README ...  done
        Generating D:\Sandbox\LibraryHippo\migrations\script.py.mako ...  done
        Please edit configuration/connection/logging settings in 'D:\\Sandbox\\LibraryHippo\\migrations\\alembic.ini' before proceeding.

        Generating D:\Sandbox\LibraryHippo\migrations\versions\b2fc8df2f32f_add_card_model.py ...  done

Insert a card into the database
-------------------------------

Normally cards would be added to the database by the users, via a fancy form. For now, the ``flask shell`` will do.

.. code:: python
    :class: m-console

    ❯ flask shell
    Python 3.8.1 (tags/v3.8.1:1b293b6, Dec 18 2019, 22:39:24) [MSC v.1916 32 bit (Intel)] on win32
    App: app [production]
    Instance: D:\Sandbox\LibraryHippo\instance
    >>> from app.models import Card, db
    >>> card = Card(patron_name="Blair Conrad", number="123456789", pin="9876")
    >>> db.session.add(card)
    >>> db.session.commit()
    >>> Card.query.all()
    [<Patron Blair Conrad>]

Load the card from the database and store the check results
===========================================================

The ``Config`` class no longer has the hard-coded patron name, card number, and
PIN values added last time, so the ``check`` route must load them from the
database and save the result back onto the card:

.. code-figure:: app/routes.py 

    .. code:: python

        # …
        import json
        from app.models import Card

        # …

        @app.route("/check")
        def check():
            card = Card.query.get(1)  # a hack - we know there's only 1 card for now
            card_check_result = WPL().check_card(card)
            card.last_state = json.dumps(card_check_result)
            db.session.commit()
            # rendering code…


The stored result can be seen by querying the database via ``flask shell``\:

.. console-figure::

    .. code:: python
        :class: m-console

        ❯ flask shell
        Python 3.8.1 (tags/v3.8.1:1b293b6, Dec 18 2019, 22:39:24) [MSC v.1916 32 bit (Intel)] on win32
        App: app [production]
        Instance: D:\Sandbox\LibraryHippo\instance
        >>> from app.models import Card
        >>> card = Card.query.get(1)
        >>> card.last_state

    .. code:: python
        :class: m-nopad

        '{"holds": [{"Title": "\\nBlood heir / Am\\u00e9lie Wen Zhao\\n\\n", "Status": " 2 of 2 holds ", "Pickup": "WPL McCormick Branch", "Cancel": "09-17-20", "Freeze": true}, {"Title": "\\nEducated : a memoir / Tara Westover\\n\\n", "Status": " 1 of 2 holds ", "Pickup": "WPL McCormick Branch", "Cancel": "09-28-20", "Freeze": true}, {"Title": "\\nCoders : the making of a new tribe and the remaking of the world / Clive Thompson\\n\\n", "Status": " 1 of 1 holds ", "Pickup": "WPL McCormick Branch", "Cancel": "10-16-20", "Freeze": true}, {"Title": "\\nBecoming Superman : my journey from poverty to Hollywood : with stops along the way at murder, mayhem, movie stars, cults, slums, sociopaths, and war crimes / J. Michael Straczynski ; introduction by Neil Gaiman\\n\\n", "Status": " 1 of 1 holds ", "Pickup": "WPL McCormick Branch", "Cancel": "11-02-20", "Freeze": true}, {"Title": "\\nBatman : Creature of the Night / illustrated by John Paul Leon.\\n\\n", "Status": " 4 of 6 holds ", "Pickup": "WPL McCormick Branch", "Cancel": "11-06-2

Use the stored card check result to send e-mail
===============================================

Now that the database contains the result of the last card status check, it's
relatively straightforward to include that text in the notification e-mails. All
that's required is to load the card record, deserialize the saved state using
``json.loads``, and build the HTML:

.. code-figure:: app/cli.py

    .. code:: python
    
        # …
        from app import mail, models

        # …

        def register(app):
            @app.cli.command("notify-all")
            def notify_all():
                card = models.Card.query.get(1)  # a hack - we know there's only 1 card for now
                last_card_state = json.loads(card.last_state)

                html_body = "<h1>Holds</h1>"
                for hold in last_card_state["holds"]:
                    html_body += "<dl>"
                    for k, v in hold.items():
                        html_body += f"<dt>{k}</dt><dd>{v}</dd>"
                    html_body += "</dl><hr>"

                html_body += "<h1>Checkouts</h1>"
                for checkout in last_card_state["checkouts"]:
                    html_body += "<dl>"
                    for k, v in checkout.items():
                        html_body += f"<dt>{k}</dt><dd>{v}</dd>"
                    html_body += "</dl><hr>"

                now = datetime.now().isoformat()

                msg = Message(
                    "LibraryHippo starting notifications", recipients=["blair@blairconrad.com"]
                )
                msg.body = f"starting notifications at {now}"
                msg.html = html_body

                mail.send(msg)

                # …

Deploy to Heroku
================

There's nothing left to do but try this out on Heroku. It shouldn't be too much work.

Add and configure a database plugin
-----------------------------------

Heroku has a free hobby-tier PostgreSQL addon that you can add on right from the command line:

.. console-figure::

    .. code:: powershell
        :class: m-console

        heroku addons:add heroku-postgresql:hobby-dev

    .. code:: text
        :class: m-nopad

        Creating heroku-postgresql:hobby-dev on ⬢ libraryhippo... free
        Database has been created and is available
        ! This database is empty. If upgrading, you can transfer
        ! data from another database with pg:copy
        Created ·················· as DATABASE_URL
        Use heroku addons:docs heroku-postgresql to view documentation

The addon sets the ``DATABASE_URL`` environment variable, which
is the one that the ``Config.SQLALCHEMY_TRACK_MODIFICATIONS`` attribute is
populated from.

SQLAlchemy needs a bonus ``psycopg2`` package to connect to the database, and
there's no harm in having it installed when I'm testing locally, so I'll just
add it to ``requirements.txt``:

.. code:: powershell
    :class: m-console

    pip install psycopg2 
    inv freeze

Finally, the application startup should perform the database migration, to react
to any new model changes. This requires an extra command before starting gunicorn:

.. code:: text

    web: flask db upgrade; gunicorn libraryhippo:app

And the only thing left to do is deploy.

Store a library card
--------------------

I'll store the library card to the PostgreSQL database just as with the local
sqlite instance. The only difference is that instead of running ``flask shell``
directly, I use Heroku's facility to run a one-off command via ``heroku run``:

.. code:: python
    :class: m-console

    ❯ heroku run flask shell
    Running flask shell on ⬢ libraryhippo... up, run.4950 (Free)
    Python 3.8.1 (default, Dec 23 2019, 04:19:22)
    [GCC 7.4.0] on linux
    App: app [production]
    Instance: /app/instance
    >>> from app.models import Card, db
    >>> card = Card(patron_name="Blair Conrad", number="123456789", pin="9876")
    >>> db.session.add(card)
    >>> db.session.commit()
    >>> Card.query.all()
    [<Patron Blair Conrad>]

With that done, there was no need to keep the old environment variables that encoded my library credentials, so I removed them:

.. code:: powershell
    :class: m-console

    heroku config:unset PATRON_NAME CARD_NUMBER PIN


Wait for the e-mail
-------------------

And that's it. I did visit ``/check`` on the website to ensure there was a
cached card status, and there was nothing else to do but wait until 18:30 local
time to see everything work together. Sure enough, the task woke up, read the
stored data, and used it in the e-mail:

.. figure:: {attach}heroku-notification-using-stored-status.png
    :alt: screenshot of notification e-mail sent from Heroku using stored card status

    Notification e-mail sent from Heroku using stored card status


Progress
========

Five of nine requirements have been met!

.. csv-table::
    :class: m-table

    :label-success:`done`, web app hosting,
    :label-success:`done`, scheduled jobs (run in UTC)
    :label-success:`done`, scraping library websites on users' behalf,
    :label-success:`done`,  small persistent datastore,
    :label-primary:`next`, social authentication,
    :label-success:`done`, sending e-mail,
       , nearly free,
       , job queues,
       , custom domain name,

