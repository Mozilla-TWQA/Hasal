python dn_nightly.py
cd ../../
activate env-python & python runtest.py --firefox-config=configs/firefox/obs_on_windows.json --index-config=configs/index/InputLatencyAnimationDctGenerator.json & cd scripts/status/ & python analyze.py & cd ../../ & python -m SimpleHTTPServer 8000
