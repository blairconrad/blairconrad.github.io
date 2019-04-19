#!/usr/bin/env python

import os.path
import sys


def main(args=sys.argv[1:]):
    title = " ".join(args)
    t = file("_template.md", "rb").read() % vars()
    basename = "".join([a.capitalize() for a in args]).translate(None, "' ")
    basename = basename[0].lower() + basename[1:]
    filename = basename + ".md"

    if os.path.exists(filename) or os.path.exists(basename + ".html"):
        raise Exception("we already have a recipe for " + title)

    with file(filename, "wb") as f:
        f.write(t)

    with file("index.md", "r") as index_in:
        index_lines = [l.strip() for l in index_in.readlines()]

    done = False
    index = 0
    for index_line in index_lines:
        if index_line.startswith("* ["):
            if index_line[3:] > title:
                index_lines.insert(index, "* [" + title + "](" + basename + ")")
                done = True
                break
        index += 1

    if not done:
        index_lines.append("* [" + title + "](" + basename + ")")

    with file("index.md", "wb") as f:
        for line in index_lines:
            f.write(line)
            f.write("\r\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
