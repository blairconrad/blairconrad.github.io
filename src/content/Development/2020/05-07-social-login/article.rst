LibraryHippo 2020 - Social Login
################################

:tags: LibraryHippo, flask, login, authomatic
:series: LibraryHippo 2020
  
I now have a functioning skeleton of a shadow LibraryHippo site. The last gaping
hole is that it treats every visitor the same. We need to be able to distinguish
one user from the next and to retain information about them between visits, such
as which family they belong to.

Rather than have users create new login identities and passwords (and worry
about securely storing those passwords), I'm going to use social logins. The old
LibraryHippo application supported login via a Google account, and I'll do the
same here, while leaving the door open to add other vectors in the future.


New Requirements
================

We'll need new software to perform the authentication and user management. The
`Flask-Login <https://flask-login.readthedocs.io/en/latest/>`_ package adds
support for storing user objects and managing their sessions, and
`Authomatic <https://authomatic.github.io/authomatic/>`_ simplifies
authentication via OAuth2 providers such as Google (and many more). Install them
both:

.. code:: powershell
    :class: m-console

    pip install Flask-Login
    pip install Authomatic
    inv freeze


Register with Google
====================

Google requires applications using it as an OAuth provider to register and
obtain credentials which must be presented when authenticating users. I visit
the
`APIs & Services Dashboard <https://console.developers.google.com/apis/dashboard>`_,
create a new project, and add a new Web application OAuth Client ID. I added 3
Authorised redirect URIs, which are the URIs that lead to the Flask route that
will handle login. Authomatic sends its current URI to Google when
authenticating, and Google redirects back to the URI (with an additional token)
after authenticating the user. As a security measure, Google will only redirect
back to known URIs.

I added

- http://localhost:5000/login/google/ (for testing locally)
- https://libraryhippo.herokuapp.com/login/google/ (for when I deploy to Heroku), and 
- http://libraryhippo.com/login/google/ (for when I eventually point the domain name to Heroku)

and was rewarded with a *Client ID* and a *Client secret*, which are needed by Authomatic.

I also configured the OAuth consent screen, which controls what users see when
they are redirected to Google. I added an application name and Application logo.
Since we only need to identify a user, I left the scopes limited to the minimum:

- email
- profile, and
- openid

I don't have an Application Privacy Policy link, so left it blank. This seems to
prevent me from "verifying" the application. So far it hasn't been an issue for
testing, but I'll keep an eye on it.

New Configuration
=================

Authomatic knows a lot about its underlying providers, but still needs to be
told about the Client ID and Client secret obtained above. I'll add those to the
``secrets`` file.

.. code-figure:: secrets

    .. code:: python

        …
        OAUTH_GOOGLE_CLIENT_ID=********.apps.googleusercontent.com
        OAUTH_GOOGLE_CLIENT_SECRET=********

Of course these need to be provided to the application through the ``Config`` class:

.. code-figure:: config.py

    .. code:: python

        from authomatic.providers import oauth2
        …

        OAUTH = {
            "google": {
                "class_": oauth2.Google,
                "consumer_key": os.environ.get("OAUTH_GOOGLE_CLIENT_ID"),
                "consumer_secret": os.environ.get("OAUTH_GOOGLE_CLIENT_SECRET"),
                "scope": ["profile", "email"],
            }
        }

        SECRET_KEY = os.environ.get("SECRET_KEY") or "MeF+3?N',Nmsn39v]"

This will tell Authomatic that there's a provider named "google" that is a
Google provider, and what the consumer ID and secret are. The "scope" entry in
the dictionary controls what Authomatic asks for from Google. If I don't specify
this, it won't load the user's email.

The other new entry, ``SECRET_KEY``, is a
`Flask concept <https://flask.palletsprojects.com/en/1.1.x/config/#SECRET_KEY>`_
that's used to sign its session cookie. It should be treated as a secret; the
default value is just supplied to make local testing easier.


The User Model
==============

Flask-Login will persist to any backing store, but the database makes the most
sense for LibraryHippo. The new ``User`` model will store the details of the
users that have been registered (by logging in):

.. code-figure:: __init__.py

    .. code:: python

        from flask_login import LoginManager
        …

        login_manager = LoginManager(app)

.. code-figure:: app/models.py

    .. code:: python

        from app import login_manager
        from flask_login import UserMixin
        …

        class User(UserMixin, db.Model):
            id = db.Column(db.Integer, primary_key=True)
            social_id = db.Column(db.String(64), nullable=False, unique=True)
            nickname = db.Column(db.String(64), nullable=False)
            email = db.Column(db.String(64), nullable=False)


        @login_manager.user_loader
        def load_user(id):
            return User.query.get(int(id))

The ``load_user`` function is registered as the Flask-Login "user_loader".
Flask-Login will ensure that there's information in the session that can
identify the active user and will use the function to load the rest of the user
information from the database.

Of course the new model has to be added via SQLAlchemy:

.. code:: powershell
    :class: m-console

    flask db migrate -m "Add User model"
    flask db upgrade


The main event - log a user in
==============================

The above has been prepatory work to allow LibraryHippo to authenticate a user
via Google, log them into Flask, and save a user record to the database.

First, I add an ``Authomatic`` instance to `app`, initializing it with the OAuth
configuration and secret key I set up earlier:

.. code-figure:: app/__init__.py

  .. code:: python

        from logging.config import dictConfig
        …
        
        authomatic = Authomatic(config=Config.OAUTH, secret=Config.SECRET_KEY)

Now add the login route, which will contain a segment for the Google provider:

.. code-figure:: app/routes.py

    .. code:: python

        from flask import flash, make_response, redirect, request, session, url_for
        from flask_login import current_user, login_user
        from authomatic.adapters import WerkzeugAdapter

        from app import authomatic
        from app.models User

        …

        @app.route("/login/<provider>/", methods=["GET", "POST"])
        def login(provider):
            if not current_user.is_anonymous:
                return redirect(url_for("index"))
        
            response = make_response()
            result = authomatic.login(
                WerkzeugAdapter(request, response),
                provider_name=provider,
                session=session,
                session_saver=lambda: app.save_session(session, response),
            )
        
            if not result:
                return response
        
            if result.user:
                result.user.update()
                if result.user.id is None:
                    flash("Authentication failed.")
                    app.logger.error("Authentication failed: %s", result.error)
                    return redirect(url_for("index"))
        
                social_id = provider + ":" + result.user.id
                user = User.query.filter_by(social_id=social_id).first()
        
            if not user:
                user = User(
                    social_id=social_id, nickname=result.user.name, email=result.user.email
                )
                db.session.add(user)
                db.session.commit()
        
            login_user(user, remember=True)
            return redirect(url_for("index"))
        
There's a lot going on here. The gist is that if the current user is logged in,
the ``login`` route just redirects to the main page; there's no need to login if
someone's already logged in.

Otherwise, Authomatic attempts to log the user in, via the ``WerkzeugAdapter``,
which lets it manipulate the HTTP request and response to direct the flow of the
application. It's given the current Flask session as well as a callback it can
use to save the session. Once that succeeds, the user is "updated" to fill in
extra information such as their name and e-mail address.

Then the method attempts to load the user from the database, looking them up by
combining the provider name and the ID assigned by the provider. If no record
exists, one is created and saved back to the database for the future. Finally,
the user is logged into Flask.

Logging out
===========

Once users are logged in, they might want to log out, maybe so another user can
check their library cards. This is much easier than the login process. Again, I
add a new route:

.. code-figure:: app/routes.py

    .. code:: python

        from flask_login import logout_user

        …

        app.route("/logout")
         logout():
            if not current_user.is_anonymous:
                logout_user()
            return redirect(url_for("index"))
        
It just calls Flask's ``logout_user`` if the user isn't logged in. Then they're
redirected to the main page.

Add login/logout links
======================

Users will need a way to initiate the login process, or to log out if they're
already logged in, and these links should be available from every page, so I'll
replace my ad hoc page generation with templates that will centralize those
functions.

.. code-figure:: app/templates/base.jinja

    .. code:: jinja

        <!DOCTYPE html>
        <html>
            <head>
                <title>LibraryHippo</title>
            </head>
            <body>
                <nav>
                {% if current_user.is_anonymous %}
                <a href="{{ url_for('login', provider='google') }}">Login</a>
                {% else %}
                <a href="{{ url_for('logout') }}">Logout {{ current_user.nickname }}</a>
                {% endif %}
                {% block body %}{% endblock %}
            </body>
        </html>

The ``base.jinja`` template sets up common elements to all the pages of the
application. Here it checks to see if the user is logged in. If not, it includes
a link to the login route, and if so, a link to the logout route. The logout
link includes the user's nickname, mostly to make it easier for me to test.
The main page has not much to add, so its template is very plain for now:

.. code-figure:: app/templates/index.jinja

    .. code:: jinja

        {% extends "base.jinja" %}

        {% block body %}
        <h1>LibraryHippo 2020</h1>
        {% endblock %}

Then the index route is updated to use the template:

.. code-figure:: app/routes.py

    .. code:: python

        from flask import render_template

        …

        @app.route("/")
        @app.route("/index")
        def index():
            return render_template("index.jinja")


How's it look?
==============

From a not-logged-in account, I visit my local LibraryHippo instance:

.. figure:: {attach}lh-not-logged-in.png
    :alt: screenshot of LibraryHippo when the user is not logged in

    LibraryHippo when the user is not logged in

The new "Login" navigation link appears. When I click it, I'm taken to a
Google-hosted page where I can select the account I want to use. This screen
will vary depending on whether I'm already logged into Google, and with how many
accounts. Note that it indicates what Google account-specific information will
be shared with LibraryHippo:

* name
* email address
* language preference (which LibraryHippo doesn't use), and
* profile picture (which LibraryHippo doesn't use)

.. figure:: {attach}lh-google-choose-account.png
    :alt: screenshot of Google asking the user to choose an account to use for login

    Google asking the user to choose an account to use for login

And finally once I'm logged in, the "Login" link becomes a "Logout" link,
including my name, which was harvested from Google.

.. figure:: {attach}lh-logged-in.png
    :alt: screenshot of LibraryHippo when the user is logged in

    LibraryHippo when the user is logged in


Deploying to Heroku
===================

There almost nothing to this. I already added the Heroku-specific URL to the
Google configuration, so I just have to generate a ``SECRET_KEY`` and set
it and the ``OAUTH_GOOGLE_CLIENT_*`` values from earlier.

.. code:: powershell
    :class: m-console

    heroku config:set OAUTH_GOOGLE_CLIENT_ID=…
    heroku config:set OAUTH_GOOGLE_CLIENT_SECRET=…
    heroku config:set SECRET_KEY=…

Progress
========

Six of nine requirements have been met!

.. csv-table::
    :class: m-table

    :label-success:`done`, web app hosting,
    :label-success:`done`, scheduled jobs (run in UTC)
    :label-success:`done`, scraping library websites on users' behalf,
    :label-success:`done`, small persistent datastore,
    :label-success:`done`, social authentication,
    :label-success:`done`, sending e-mail,
       , nearly free,
       , job queues,
       , custom domain name,

