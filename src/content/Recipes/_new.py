#!/usr/bin/env python

import os.path
import sys


def main(args=sys.argv[1:]):
    title = " ".join(args)
    basename = "".join([a.capitalize() for a in args]).translate(
        str.maketrans("", "", "' ")
    )
    basename = basename[0].lower() + basename[1:]
    filename = basename + ".md"

    if os.path.exists(filename) or os.path.exists(basename + ".html"):
        raise Exception("we already have a recipe for " + title)

    with open("_template.md", "r") as template:
        content = template.read() % vars()
        with open(filename, "w") as new_recipe_file:
            new_recipe_file.write(content)

    return 0


if __name__ == "__main__":
    sys.exit(main())
