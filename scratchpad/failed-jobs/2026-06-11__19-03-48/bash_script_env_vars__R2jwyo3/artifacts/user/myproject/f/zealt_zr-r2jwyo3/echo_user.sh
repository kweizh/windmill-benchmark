#!/bin/bash
# echo_user: consumes a positional string argument and the WM_USERNAME env var,
# printing a single JSON object as the last line of stdout.

input="$1"
user="$WM_USERNAME"

echo "{\"input\": \"$input\", \"user\": \"$user\"}"
