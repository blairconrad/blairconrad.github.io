#!/usr/bin/env python

import os.path
import sys


def main(args=sys.argv[1:]):
    title = ' '.join(args)
    t = file('_template.md', 'rb').read() % vars()
    basename = (''.join([a.capitalize() for a in args])
                .translate(None, "' "))
    basename = basename[0].lower() + basename[1:]
    filename = basename + '.md'

    if os.path.exists(filename) or os.path.exists(basename + '.html'):
        raise Exception('we already have a recipe for ' + title)

    with file(filename, 'wb') as f:
        f.write(t)

    return 0


if __name__ == '__main__':
    sys.exit(main())
