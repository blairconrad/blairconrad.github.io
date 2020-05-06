# -*- coding: utf-8 -*-

import os
import shutil
import sys
import datetime

from invoke import task
from invoke.util import cd
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
    "github_pages_branch": "master",
    "commit_message": "'Publish site on {}'".format(datetime.date.today().isoformat()),
    # Port for `serve`
    "port": 8000,
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
    server.serve(port=CONFIG["port"], root=CONFIG["deploy_path"])


@task
def publish(c, token=""):
    """Publish today's draft, if any"""
    if not token:
        raise Exception("No GITHUB_TOKEN supplied")

    github_actor = os.environ.get("GITHUB_ACTOR")
    if not github_actor:
        raise Exception("No GITHUB_ACTOR supplied")

    repository = os.environ.get("GITHUB_REPOSITORY")
    if not repository:
        raise Exception("No REPOSITORY supplied")

    now = datetime.datetime.utcnow()
    today_path = os.path.join(
        "..", "drafts", now.strftime("%Y"), now.strftime("%m"), now.strftime("%d")
    )

    print(f"Looking for draft at {today_path}.")
    if not os.path.exists(today_path):
        print("No draft found. Exiting.")
        return

    preview(c)

    now_slug = now.strftime("%Y-%m-%d")

    c.run('git config --local user.email "blair@blairconrad.com"', warn=True)
    c.run('git config --local user.name "Blair Conrad"', warn=True)
    c.run(f"git checkout -b publish-{now_slug}", warn=True)
    c.run("git add -A ..", warn=True)
    c.run(f'git commit -m "Publish article from {now_slug}"', warn=True)
    c.run("git checkout master", warn=True)
    c.run(f"git merge --no-ff publish-{now_slug}", warn=True)

    remote_repo = f"https://{github_actor}:{token}@github.com/{repository}.git"
    print(f"remote_repo = {remote_repo}")
    c.run(f"git push {remote_repo} HEAD:master")


@task
def gh_pages(c):
    """Publish to GitHub Pages"""
    preview(c)
    c.run(
        "ghp-import -b {github_pages_branch} "
        "-m {commit_message} "
        "{deploy_path} -p".format(**CONFIG)
    )
