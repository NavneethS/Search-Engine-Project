#!/bin/bash

# Unsorted temporary index to sorted form on disk
for file in ./unsortedchunks/*; do
    sort -S 75% $file -o "./sortedchunks/${file##*/}"
    echo "$file done"
done

# Sorted temporary index to single merged file on disk separated into chunks of size 2M lines each
sort -m ./sortedchunks/* | split -l 2000000 - mergedchunks_m/x
~
