#!/bin/bash
#Should give a test suite file to execute cases
if [ -z "$1" ]; then
  echo "Test suite file is needed"
  exit 1
fi

while IFS='' read -r case_name || [[ -n "$case_name" ]]; do
  case_name_no_space="$(echo -e "$case_name" | tr -d '[[:space:]]')"
  if [ -z $case_name_no_space ]; then
    continue
  fi
  COUNTER=0
  RETRY_COUNTER=0
  while [ $COUNTER -lt 30 ]; do
    pkill firefox
    pkill chrome
    pkill avconv
    echo "The counter is $COUNTER and the retry_counter is $RETRY_COUNTER"
    python -m unittest tests.$case_name_no_space
    break
    out=$?
    if [ "$out" -eq 0 ]; then
      let COUNTER=COUNTER+1
    else
      let RETRY_COUNTER=RETRY_COUNTER+1
      if [ "$RETRY_COUNTER" -ge 15 ]; then
        break
      fi
    fi
  done
done < "$1"
#Should do a signal in order to show that this is end
gedit end.txt
