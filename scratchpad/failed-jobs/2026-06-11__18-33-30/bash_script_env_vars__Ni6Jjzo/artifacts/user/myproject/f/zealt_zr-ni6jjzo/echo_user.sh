#!/bin/bash
# echo_user - Prints input and WM_USERNAME as JSON
INPUT="$1"
USERNAME="${WM_USERNAME}"
printf '{"input":"%s","user":"%s"}\n' "$INPUT" "$USERNAME"