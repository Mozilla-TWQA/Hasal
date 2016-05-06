#!/bin/bash
#Should give a test suite file to execute cases

if [ -z "$1" ]; then
  echo "Test suite file is needed"
  exit 1
fi

if [ -z "$2" ]; then
  MAX_RUN=40
else
  MAX_RUN=$2
fi

if [ -z "$3" ]; then
  MAX_RETRY=15
else
  MAX_RETRY=$3
fi

while IFS='' read -r case_name || [[ -n "$case_name" ]]; do
  case_name_no_space="$(echo -e "$case_name" | tr -d '[[:space:]]')"
  if [ -z $case_name_no_space ]; then
    continue
  fi
  COUNTER=0
  RETRY_COUNTER=0
  while [ $COUNTER -lt $MAX_RUN ]; do
    pkill firefox
    pkill chrome
    pkill avconv
    echo "The counter is $COUNTER and the retry_counter is $RETRY_COUNTER"
    python -m unittest tests.$case_name_no_space
    sikuli_stat=$(head -n 1 sikuli_stat.txt)
    if [ "$sikuli_stat" -eq 0 ]; then
      let COUNTER=COUNTER+1
    else
      let RETRY_COUNTER=RETRY_COUNTER+1
      if [ "$RETRY_COUNTER" -ge $MAX_RETRY ]; then
        break
      fi
    fi
  done
done < "$1"
#Should do a signal in order to show that this is end
gedit end.txt
