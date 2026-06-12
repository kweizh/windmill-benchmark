#!/bin/bash
INPUT=$1
jq -n -c --arg input "$INPUT" --arg user "$WM_USERNAME" '{input: $input, user: $user}'
