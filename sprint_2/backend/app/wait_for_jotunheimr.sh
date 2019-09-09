#!/bin/bash

host="$1"
shift
cmd="$@"

echo 'Wait for '$host' ...'
end="$((SECONDS+10))"
while ! nc -z $host 7474; do
  [[ "${SECONDS}" -ge "${end}" ]] && exit 1
  sleep 1
done

echo "Done."

exec $cmd
