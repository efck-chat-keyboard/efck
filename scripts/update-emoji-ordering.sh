#!/bin/sh
set -eux

UNICODE_VERSION=14.0

cd "$(dirname $0)/../efck"
curl -O "https://unicode.org/emoji/charts-${UNICODE_VERSION}/emoji-ordering.txt"
