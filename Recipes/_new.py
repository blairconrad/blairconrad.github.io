#!/usr/bin/env python

import sys
import subprocess

def main(args=sys.argv[1:]):
    title = ' '.join(args)
    t = file('_template.md', 'rb').read() % vars()
    filename = ''.join([a.capitalize() for a in args]).replace("'", "").replace(" ", "")
    filename = filename[0].lower() + filename[1:] + '.md'

    with file(filename, 'wb') as f:
        f.write(t)

    return 0


if __name__ == '__main__':
    sys.exit(main())

