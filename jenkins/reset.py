import os
import sys

conf_path = os.path.join(sys.argv[1], "agent", "hasal.json")
if os.path.exists(conf_path):
    os.remove(conf_path)
