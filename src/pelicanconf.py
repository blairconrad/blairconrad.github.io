#!/usr/bin/env python
# -*- coding: utf-8 -*- #

import os

PATH = "content"
OUTPUT_PATH = "../_local_build"

SITENAME = "Blair Conrad"
SITEURL = ""

TIMEZONE = "America/Toronto"

DEFAULT_LANG = "en"
DEFAULT_DATE_FORMAT = "%Y-%m-%d"

PLUGIN_PATHS = ["plugins"]
PLUGINS = ["series"]

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

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


DEFAULT_PAGINATION = 10
DEFAULT_ORPHANS = 3
PAGINATION_PATTERNS = (
    (1, "{url}", "{save_as}"),
    (2, "{base_name}/page/{number}/", "{base_name}/page/{number}/index.html"),
)

DISPLAY_PAGES_ON_MENU = False

STATIC_PATHS = ["images", "Recipes", "extra"]

PAGE_PATHS = ["pages", "Recipes"]
EXTRA_PATH_METADATA = {}
for (path, directories, files) in os.walk(os.path.join("content", "extra")):
    for f in files:
        full_path = (path + "/" + f).replace("\\", "/")
        EXTRA_PATH_METADATA[full_path[8:]] = {"path": full_path[14:]}

THEME_TEMPLATES_OVERRIDES = ["templates"]

THEME = "m.css/pelican-theme"
DIRECT_TEMPLATES = ["index", "Recipes", "404"]
RECIPES_SAVE_AS = "Recipes/index.html"

THEME_STATIC_DIR = "static"

M_HIDE_ARTICLE_SUMMARY = True

M_CSS_FILES = [
    "/static/m-dark.css",
    "https://fonts.googleapis.com/css?family=Open+Sans:400,400i,600,600i%7CFira+Code:400,400i,600",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.12.0/css/all.min.css",
    "/static/custom.css",
]

M_THEME_COLOR = "#22272e"

PLUGIN_PATHS += ["m.css/plugins"]
PLUGINS += ["m.htmlsanity", "m.code", "m.components", "m.images"]


M_LINKS_NAVBAR1 = [("Recipes", "Recipes/", "recipes", [])]
