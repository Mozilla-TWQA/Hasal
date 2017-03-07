import os
import json


def dump_data_to_json_file(input_json_fp, input_data):
    if os.path.exists(input_json_fp):
        with open(input_json_fp, "r+") as fh:
            stat_data = json.load(fh)
            stat_data.update(input_data)
            fh.seek(0)
            fh.write(json.dumps(stat_data))
    else:
        with open(input_json_fp, 'w') as fh:
            fh.write(json.dumps(input_data))