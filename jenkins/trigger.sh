#!/bin/bash
# HASAL_WORKSPACE is the Hasal path in current environment

cd $HASAL_WORKSPACE

git checkout master
pip install treeherder-client==3.0.0
pip install docopt

git pull
python tools/trigger_build.py
