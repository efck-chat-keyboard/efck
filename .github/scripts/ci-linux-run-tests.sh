#!/bin/sh
# Run tests under X with a window manager
# We check test.log in case Qt segfaulted on exit
set -eux
xvfb-run -a -- sh -c '
    set -eux
    flwm &
    trap "kill $!" EXIT
    time coverage run -m efck.tests -v
'
