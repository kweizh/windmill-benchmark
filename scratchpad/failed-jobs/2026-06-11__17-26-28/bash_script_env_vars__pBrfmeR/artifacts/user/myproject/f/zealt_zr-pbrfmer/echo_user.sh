# shellcheck shell=bash
# arguments of the form X="$I" are parsed as parameters X of type string
input="$1"

echo "{\"input\": \"$input\", \"user\": \"$WM_USERNAME\"}"
