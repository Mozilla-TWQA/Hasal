::HASAL_WORKSPACE is the Hasal path in current environment

cd %HASAL_WORKSPACE%

git checkout master
pip install -Ur tools/requirements.txt

git pull
python tools\trigger_build.py
