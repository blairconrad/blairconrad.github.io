#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

# This file is only used if you use `make publish` or
# explicitly specify it as your config file.

import os
import sys

sys.path.append(os.curdir)
from pelicanconf import *

OUTPUT_PATH = ".."
OUTPUT_RETENTION = [".git", ".gitignore", ".nojekyll", "src", "README.md"]

# If your site is available via HTTPS, make sure SITEURL begins with https://
SITEURL = "https://blairconrad.com"
RELATIVE_URLS = False

FEED_ALL_ATOM = "feeds/all.atom.xml"
CATEGORY_FEED_ATOM = "feeds/{slug}.atom.xml"

DELETE_OUTPUT_DIRECTORY = True

# Following items are often useful when publishing

# DISQUS_SITENAME = ""
# GOOGLE_ANALYTICS = ""

M_CSS_FILES.remove("/static/m-dark.css")
M_CSS_FILES.insert(0, "/static/m-dark.compiled.css")
