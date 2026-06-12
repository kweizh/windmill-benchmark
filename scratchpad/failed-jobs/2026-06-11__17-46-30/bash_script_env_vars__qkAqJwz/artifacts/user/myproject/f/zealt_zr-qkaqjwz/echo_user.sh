#!/bin/bash
# <name>echo_user</name>
# <description>Echoes the input argument along with the caller's WM_USERNAME</description>

input="$1"

echo "{\"input\": \"${input}\", \"user\": \"${WM_USERNAME}\"}"
