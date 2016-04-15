#!/bin/bash

COUNTER=0
while [ $COUNTER -lt 40 ]; do
  echo "The counter is $COUNTER"
  python -m unittest tests.test_firefox_gdoc_pagedown
  let COUNTER=COUNTER+1
done

COUNTER=0
while [ $COUNTER -lt 40 ]; do
  echo "The counter is $COUNTER"
  python -m unittest tests.test_chrome_gdoc_pagedown
  let COUNTER=COUNTER+1
done

#Should do a signal in order to show that this is end
gedit end.txt
