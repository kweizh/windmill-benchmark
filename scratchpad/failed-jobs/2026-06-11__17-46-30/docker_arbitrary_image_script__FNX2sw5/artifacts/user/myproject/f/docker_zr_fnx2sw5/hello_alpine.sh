# shellcheck shell=bash
# sandbox alpine:3
message="$1"
. /etc/os-release
echo "hello $message from $NAME"
