# -*- coding: utf-8 -*-

import os
import sys
import datetime

from invoke import task
from pelican.server import ComplexHTTPRequestHandler, RootedHTTPServer
from pelican.settings import DEFAULT_CONFIG, get_settings_from_file

SETTINGS_FILE_BASE = "pelicanconf.py"
SETTINGS = {}
SETTINGS.update(DEFAULT_CONFIG)
LOCAL_SETTINGS = get_settings_from_file(SETTINGS_FILE_BASE)
SETTINGS.update(LOCAL_SETTINGS)

CONFIG = {
    "settings_base": SETTINGS_FILE_BASE,
    "settings_publish": "publishconf.py",
    # Output path. Can be absolute or relative to tasks.py. Default: 'output'
    "deploy_path": SETTINGS["OUTPUT_PATH"],
    # Github Pages configuration
    "github_pages_branch": "main",
    "commit_message": "'Publish site on {}'".format(datetime.date.today().isoformat()),
    # Port for `serve`
    "port": 8000,
    # The IP to which to bind the HTTP server.
    "bind": SETTINGS["BIND"],
}


@task
def build(c):
    """Build local version of site"""
    c.run("pelican -s {settings_base}".format(**CONFIG))


@task
def rebuild(c):
    """`build` with the delete switch"""
    c.run("pelican -s {settings_base}".format(**CONFIG))


@task
def regenerate(c):
    """Automatically regenerate site upon file modification"""
    c.run("pelican -r -s {settings_base}".format(**CONFIG))


@task
def serve(c):
    """Serve site at http://localhost:$PORT/ (default port is 8000)"""

    class AddressReuseTCPServer(RootedHTTPServer):
        allow_reuse_address = True

    server = AddressReuseTCPServer(
        CONFIG["deploy_path"], ("", CONFIG["port"]), ComplexHTTPRequestHandler
    )

    sys.stderr.write("Serving on port {port} ...\n".format(**CONFIG))
    server.serve_forever()


@task
def reserve(c):
    """`build`, then `serve`"""
    build(c)
    serve(c)


@task
def clean(c):
    """Remove all generated output"""
    import publishconf
    import shutil

    for f in os.listdir(".."):
        if f in publishconf.OUTPUT_RETENTION:
            continue
        f = os.path.join("..", f)
        if os.path.isdir(f):
            shutil.rmtree(f)
        else:
            os.remove(f)


@task(clean)
def preview(c):
    """Build production version of site"""
    c.run("pelican -d -s {settings_publish}".format(**CONFIG), warn=True)


@task
def livereload(c):
    """Automatically reload browser tab upon file modification."""

    # A custom watcher to workaround a bug in the livereload glob detection
    # From https://github.com/lepture/python-livereload/issues/156
    import glob
    from livereload.watcher import Watcher

    class CustomWatcher(Watcher):
        def is_glob_changed(self, path, ignore=None):
            for f in glob.glob(path, recursive=True):
                if self.is_file_changed(f, ignore):
                    return True
            return False

    import asyncio

    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy()
    )  # python-3.8.0a4
    from livereload import Server

    build(c)
    server = Server(watcher=CustomWatcher())
    # Watch the base settings file
    server.watch(CONFIG["settings_base"], lambda: build(c))
    # Watch content source files
    content_file_extensions = [".md", ".rst"]
    for extension in content_file_extensions:
        content_blob = "{0}/**/*{1}".format(SETTINGS["PATH"], extension)
        server.watch(content_blob, lambda: build(c))
    # Watch the theme's templates and static assets
    theme_path = SETTINGS["THEME"]
    server.watch("{}/templates/*.html".format(theme_path), lambda: build(c))
    static_file_extensions = [".css", ".js"]
    for extension in static_file_extensions:
        static_file = "{0}/static/**/*{1}".format(theme_path, extension)
        server.watch(static_file, lambda: build(c))

    # Watch additional templates and static assets
    for template_overrides_path in SETTINGS["THEME_TEMPLATES_OVERRIDES"]:
        template = "{}/*".format(template_overrides_path)
        print("watching", template)
        server.watch(template, lambda: build(c))
    for extension in static_file_extensions:
        for static_path in SETTINGS["STATIC_PATHS"]:
            static_file = "{0}/{1}/**/*{2}".format(
                SETTINGS["PATH"], static_path, extension
            )
            print("watching", static_file)
            server.watch(static_file, lambda: build(c))

    # Serve output path on configured port
    server.serve(host=CONFIG["bind"], port=CONFIG["port"], root=CONFIG["deploy_path"])


@task
def recipe(c, name):
    '''Create a new recipe, like: recipe "A Delicious Cake"'''
    name_parts = name.split()
    title = " ".join(name_parts)
    basename = "".join([a.capitalize() for a in name_parts]).translate(
        str.maketrans("", "", "' ")
    )

    basename = basename[0].lower() + basename[1:] + ".md"
    filename = os.path.join("content", "Recipes", basename)

    if os.path.exists(filename):
        raise Exception("we already have a recipe for " + title)

    template_file = os.path.join("templates", "recipe.md")
    with open(template_file, "r") as template:
        content = template.read() % vars()
        with open(filename, "w") as new_recipe_file:
            new_recipe_file.write(content)


@task
def compile_requirements(c, upgrade=False):
    """
    Build new requirements/*.txt files from corresponding requirements/*.in files
    """
    command = "pip-compile"
    if upgrade:
        command += " --upgrade"
    with c.cd('requirements'):
        for in_file in ["prod", "dev"]:
            c.run(f"{command} {in_file}.in")
