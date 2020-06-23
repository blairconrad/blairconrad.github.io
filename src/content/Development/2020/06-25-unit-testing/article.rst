LibraryHippo 2020 - Unit Tests
##############################


:tags: LibraryHippo, requests-mock, testing
:series: LibraryHippo 2020


Now that I've completed all my
`spikes <http://www.extremeprogramming.org/rules/spike.html>`_ and decided to
move forward, I'd like to add a little more rigour to the project. Original
LibraryHippo had a comprehensive suite of unit tests and I'll port them over
(and perhaps augment them with integration tests). Today I'll add the first unit
test to the project, then port over a bunch more when you're not looking!


Prerequisites
=============

The first thing we need is a test-running package. My favourite is
`pytest <https://docs.pytest.org/en/latest/>`_.

.. code:: powershell
    :class: m-console

    ❯ pip install pytest
    ❯ inv freeze


Now I need a place to put the tests. I'll broadly be following the structure
from Patrick Kennedy's
`Testing a Flask Application using pytest <https://www.patricksoftwareblog.com/testing-a-flask-application-using-pytest/>`_,
although most of it won't be needed today, so I'll just make the ``tests\unit``
structure, including empty ``__init__.py`` files so my imports work.

.. code:: powershell
    :class: m-console

    ❯ 'tests', 'tests\unit' | ForEach-Object {
        New-Item -Type File $_\__init__.py -Force
    }

First test
==========

Next, I write a simple unit test for the ``WPL`` class, to make sure it correctly reads the items I have on hold.

.. code-figure:: tests/unit/test_wpl.py

    .. code:: python

        from app.libraries.wpl import WPL
        from app.models import Card


        def test_check_card_finds_holds():
            card = make_card()

            target = WPL()
            check_result = target.check_card(card)

            assert check_result is not None
            assert check_result["holds"]


        def make_card():
            card = Card()
            card.patron_name = "Blair Conrad"
            card.number = "123456789"
            card.pin = "9876"
            return card

Run it using ``pytest``, and success!

.. include:: pytest.ansi
    :code: ansi

Isolate tests from the library website
======================================

That test shows that the code is doing something, but it's dependent on
responses from the Waterloo Public Library website. If I don't have any holds,
or the site is down, my test will fail. I'll use
`requests-mock <https://requests-mock.readthedocs.io/en/latest/>`_ to fake out
interactions with the library system.

.. code-block:: powershell

    ❯ pip install requests-mock
    ❯ inv freeze

I'd never used requests-mock before, and it was incredibly easy. It provides a
pytest fixture on which I can set expectations for the requests module. Within
minutes, I'd used the ``mock_requests`` fixture to configure fake results for

1. getting the login page
2. posting the login page
3. getting the holds page
4. getting the checkouts page

.. code-figure:: tests/unit/test_wpl.ca

    .. code:: python

        def test_check_card_finds_holds(requests_mock):
            login_url = (
                "https://books.kpl.org/iii/cas/login?service="
                + "https://books.kpl.org/patroninfo~S3/"
                + "j_acegi_cas_security_check&lang=eng&scope=3"
            )

            requests_mock.get(login_url, text="")
            requests_mock.post(login_url, text="<a href='/holds'>holds</a>")

            requests_mock.get(
                "/holds",
                text="""
                    <table class="patFunc">
                    <tr class="patFuncHeaders"><th> TITLE </th><th>STATUS</th></tr>
                    <tr class="patFuncEntry">
                        <td class="patFuncTitle">Blood heir / Amélie Wen Zhao</td>
                        <td class="patFuncStatus"> 9 of 83 holds </td>
                    </tr>
                    </table>
                    """,
            )

            card = make_card()

            target = WPL()
            check_result = target.check_card(card)

            assert check_result
            assert check_result["holds"]
            assert check_result["holds"][0] == {
                "Status": " 9 of 83 holds ",
                "Title": "Blood heir / Amélie Wen Zhao",
            }

This passes just as in its previous iteration, even after I made the test more
specific. Since I control the "response from the library", I can expect a
particular held item to be present. In the future, this will allow me to easily
verify that holds with different statuses, such as "in transit" or "missing" are
reported properly.

A note on mocking styles
========================

As a maintainer of the
`third most popular and first best .NET mocking framework <https://fakeiteasy.github.io/>`_,
I have opinions on mocking practices. For one, I generally advise against
`monkey patching <https://www.geeksforgeeks.org/monkey-patching-in-python-dynamic-behavior/>`_
or anything else that seems like magic. I've worked in environments where these
effects were abused, and tests became very difficult to debug.

The new test relies on a magically-provided ``requests_mock`` object, and
actions on that object affect the functioning of the ``requests`` module. This
gave me pause. Ultimately, I decided to go with it, for two reasons. First, the
`pytest fixtures <https://docs.pytest.org/en/latest/fixture.html>`_ have
well-known behaviour and should undo the ``requests_mock``'s changes after every
test function. Second, the actual monkey patching is too convenient to not try.
I toyed with the idea of adding a fixture that created a new session, had
requests-mock intercept only that, and then pass both those objects to each
test, and it just seemed like too much work for the benefit. Hopefully, as sole
maintainer on LibraryHippo, I'll be able to keep a handle on the magic mocking.
If not, I can always fall back to a more explicit style.



