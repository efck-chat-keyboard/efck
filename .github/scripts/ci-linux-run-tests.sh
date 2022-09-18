#!/bin/sh
# Run tests under X with a window manager
# We check test.log in case Qt segfaulted on exit
set -eu
xvfb-run -- sh -c '
    flwm &
    trap "kill $!" EXIT
    time catchsegv coverage run -m efck.tests -v | tee test.log ||
        grep -Pq "^OK$" test.log
        '
