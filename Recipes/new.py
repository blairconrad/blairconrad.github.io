#!/usr/bin/env python

import sys
import subprocess

def main(args=sys.argv[1:]):
    title = ' '.join(args)
    t = file('template.html', 'rb').read() % vars()
    filename = ''.join(args).replace("'", "").replace(" ", "")
    filename = filename[0].lower() + filename[1:] + '.html'

    with file(filename, 'wb') as f:
        f.write(t)

    subprocess.call(['svn', 'add', filename])
    subprocess.call(['svn', 'propset', 'svn:mime-type', 'text/html', filename])
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

