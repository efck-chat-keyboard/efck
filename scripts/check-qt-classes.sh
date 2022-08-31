#!/bin/bash

set -eu

cd "$(dirname $0)/../efck"
qregex='\bQ([A-Z][a-z]+)+\b'
used_classes="$(grep -PRo --no-filename $qregex **/*.py --exclude=*/_qt/* | sort -u)"
for file in _qt/*.py; do
    available_classes="$(grep -PRo --no-filename $qregex $file | sort -u)"
    diff="$(comm -3 <(echo "$used_classes") <(echo "$available_classes"))"
    if [ "$diff" ]; then
        echo -e "\nERROR: Some Qt classes used (but not available in '$file') or vice versa.\n"
        echo -e 'Used\tAvail'
        echo "$diff"
        exit 1
    fi
    echo "$file ok"
done
echo 'All ok! Bye'
