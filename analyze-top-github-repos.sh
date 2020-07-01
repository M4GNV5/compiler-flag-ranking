#!/bin/bash

python3 extract-options.py

function retrieve_page
{
    curl "https://api.github.com/search/repositories?q=language:c&sort=stars&order=desc&per_page=100&page=$1" \
        | jq -r '.items[].full_name' \
        >> repositories.list
}

rm repositories.list
#for i in $(seq 1 10); do
#    retrieve_page "$i"
#done
retrieve_page 10

python3 analyze-github-repos.py
