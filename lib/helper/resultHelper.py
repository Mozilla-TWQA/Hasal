import os
import json
from ..common.imageTool import ImageTool


def run_image_analyze(input_video_fp, output_img_dp, input_sample_dp):
    if os.path.exists(output_img_dp) is False:
        os.mkdir(output_img_dp)
    img_tool_obj = ImageTool()
    img_tool_obj.convert_video_to_images(input_video_fp, output_img_dp)
    return img_tool_obj.compare_with_sample_image(input_sample_dp)


def output_result(test_method_name,current_run_result, output_fp):
    # result = {'class_name': {'total_run_no': 0, 'error_no': 0, 'total_time': 0, 'avg_time': 0, 'max_time': 0, 'min_time': 0, 'detail': []}}
    run_time = 0
    if os.path.exists(output_fp):
        with open(output_fp) as fh:
            result = json.load(fh)
    else:
        result = {}

    if len(current_run_result) == 2:
        run_time = current_run_result[0]['time_seq'] - current_run_result[1]['time_seq']

    if test_method_name in result:
        result[test_method_name]['total_run_no'] += 1
        result[test_method_name]['total_time'] += run_time
        if run_time == 0:
            result[test_method_name]['error_no'] += 1
        if (result[test_method_name]['total_run_no'] - result[test_method_name]['error_no']) == 0:
            result[test_method_name]['avg_time'] = 0
        else:
            result[test_method_name]['avg_time'] = result[test_method_name]['total_time'] / (result[test_method_name]['total_run_no'] - result[test_method_name]['error_no'])
        if run_time > result[test_method_name]['max_time']:
            result[test_method_name]['max_time'] = run_time
        if run_time < result[test_method_name]['min_time']:
            result[test_method_name]['min_time'] = run_time
        result[test_method_name]['detail'].extend(current_run_result)
    else:
        result[test_method_name] = {}
        result[test_method_name]['total_run_no'] = 1
        result[test_method_name]['total_time'] = run_time
        if run_time == 0:
            result[test_method_name]['error_no'] = 1
            result[test_method_name]['avg_time'] = 0
            result[test_method_name]['max_time'] = 0
            result[test_method_name]['min_time'] = 0
        else:
            result[test_method_name]['error_no'] = 0
            result[test_method_name]['avg_time'] = run_time
            result[test_method_name]['max_time'] = run_time
            result[test_method_name]['min_time'] = run_time
        result[test_method_name]['detail'] = current_run_result

    with open(output_fp, "wb") as fh:
        json.dump(result, fh, indent=2)


def result_calculation(env):
    current_data = run_image_analyze(env.video_output_fp, env.img_output_dp, env.img_sample_dp)
    output_result(env.test_method_name, current_data, env.DEFAULT_TEST_RESULT)
