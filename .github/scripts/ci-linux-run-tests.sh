#!/bin/sh
# Run tests under X with a window manager
# We check test.log in case Qt segfaulted on exit
set -eux
xvfb-run -a -- bash -c '
    set -eux
    set -o pipefail
    flwm &
    trap "set +e; kill $!" EXIT
    time catchsegv coverage run -m efck.tests -v |& tee /tmp/test.log
'
grep -Pq '^OK$' /tmp/test.log
