python dn_nightly.py
cd \Users\user\Hasal\
activate env-python & python runtest.py --firefox-config=configs/firefox/obs_on_windows.json --index-config=configs/index/InputLatencyAnimationDctGenerator.json & cd\Users\user\Hasal\scripts\status & python analyze.py & cd \Users\user\Hasal\ & python -m SimpleHTTPServer 8000