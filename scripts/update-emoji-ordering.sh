#!/bin/sh
set -eux

UNICODE_VERSION=17.0  # FIXME: Figure out how to bump this automatically

cd "$(dirname $0)/../efck"
curl -O "https://unicode.org/emoji/charts-${UNICODE_VERSION}/emoji-ordering.txt"
