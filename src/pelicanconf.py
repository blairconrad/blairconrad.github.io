#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = "Blair Conrad"
SITENAME = "Blair Conrad"
SITEURL = ""
# LANDING_PAGE_TITLE = "Blair Conrad"

PROJECTS = [
    {
        "name": "FakeItEasy - The easy mocking library for .NET",
        "url": "https://fakeiteasy.github.io/",
        "description": "A .Net dynamic fake framework for creating all types of fake objects, mocks, stubs etc.",
    },
    {
        "name": "LibraryHippo",
        "url": "http://libraryhippo.com/",
        "description": "Monitor your family's library accounts at the: Waterloo Public Library, Kitchener Public Library, and Region of Waterloo Library",
    },
]

PATH = "content"
OUTPUT_PATH = "../_local_build"
THEME = "themes/elegant"


TIMEZONE = "America/Toronto"

DEFAULT_LANG = "en"
DEFAULT_DATE_FORMAT = "%Y-%m-%d"

PLUGIN_PATHS = ["plugins"]
PLUGINS = ["neighbors", "series"]

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (
    ("Pelican", "http://getpelican.com/"),
    ("Python.org", "http://python.org/"),
    ("Jinja2", "http://jinja.pocoo.org/"),
    ("You can modify those links in your config file", "#"),
)

# Social widget
SOCIAL = (
    ("Github", "http://github.com/blairconrad"),
    ("Twitter", "http://twitter.com/hippopottoman"),
    ("Goodreads", "https://www.goodreads.com/user/show/1066544-blair-conrad"),
)

SLUGIFY_SOURCE = "title"
ARTICLE_URL = "{date:%Y}/{date:%m}/{date:%d}/{slug}/"
ARTICLE_SAVE_AS = "{date:%Y}/{date:%m}/{date:%d}/{slug}/index.html"
PAGE_URL = "pages/{slug}/"
PAGE_SAVE_AS = "pages/{slug}/index.html"
SLUG_REGEX_SUBSTITUTIONS = [
    (r"[^\w\s.-]", ""),  # remove non-alphabetical/whitespace/'.'/'-' chars
    (r"(?u)\A\s*", ""),  # strip leading whitespace
    (r"(?u)\s*\Z", ""),  # strip trailing whitespace
    (r"[-\s]+", "-"),  # reduce multiple whitespace or '-' to single '-'
]


THEME_TEMPLATES_OVERRIDES = ["templates"]
DIRECT_TEMPLATES = [
    "index",
    "tags",
    "categories",
    "authors",
    "archives",
    "404",
    "Recipes",
]
RECIPES_SAVE_AS = "Recipes/index.html"

DEFAULT_PAGINATION = False

# Uncomment following line if you want document-relative URLs when developing
RELATIVE_URLS = True


DISPLAY_PAGES_ON_MENU = False

STATIC_PATHS = ["images", "css", "Recipes", "extra/keybase.txt", "extra/CNAME"]

PAGE_PATHS = ["pages", "Recipes"]

EXTRA_PATH_METADATA = {
    "extra/CNAME": {"path": "CNAME"},
    "extra/keybase.txt": {"path": "keybase.txt"},
    "images/favicon.ico": {"path": "favicon.ico"},
}
