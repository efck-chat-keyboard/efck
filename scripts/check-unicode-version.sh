#!/bin/sh
curl --no-progress-meter https://www.unicode.org/versions/latest/ |
    grep -q Unicode17
