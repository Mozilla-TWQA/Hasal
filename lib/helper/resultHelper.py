import os
import json
from collections import Counter
from ..common.imageTool import ImageTool
from ..common.outlier import outlier
import numpy as np
import re
from ..common.logConfig import get_logger

logger = get_logger(__name__)


def run_image_analyze(input_video_fp, output_img_dp, input_sample_dp, exec_timestamp_list, crop_data=None, fps=0, calc_si=0):
    return_result = {}
    if os.path.exists(output_img_dp) is False:
        os.mkdir(output_img_dp)
    img_tool_obj = ImageTool(fps=fps)
    if crop_data:
        img_tool_obj.convert_video_to_images(input_video_fp, output_img_dp, None, exec_timestamp_list, True)
        img_tool_obj.crop_image(crop_data['target'], crop_data['output'], crop_data['range'])
        return_result['running_time_result'] = img_tool_obj.compare_with_sample_object(input_sample_dp)
    else:
        if calc_si == 0:
            img_tool_obj.convert_video_to_images(input_video_fp, output_img_dp, None, exec_timestamp_list)
        else:
            img_tool_obj.convert_video_to_images(input_video_fp, output_img_dp, None, exec_timestamp_list, True)
        return_result['running_time_result'] = img_tool_obj.compare_with_sample_image(input_sample_dp)
    if calc_si == 1:
        si_progress = img_tool_obj.calculate_progress_for_si(return_result['running_time_result'])
        return_result['speed_index'] = img_tool_obj.calculate_speed_index(si_progress)
        return_result['perceptual_speed_index'] = img_tool_obj.calculate_perceptual_speed_index(si_progress)
    return return_result


def output_result(test_method_name, result_data, output_fp, time_list_counter_fp, test_method_doc, outlier_check_point, video_fp, web_app_name):
    # result = {'class_name': {'total_run_no': 0, 'error_no': 0, 'total_time': 0, 'avg_time': 0, 'max_time': 0, 'min_time': 0, 'time_list':[] 'detail': []}}
    run_time = 0
    if os.path.exists(output_fp):
        with open(output_fp) as fh:
            result = json.load(fh)
    else:
        result = {}

    current_run_result = result_data['running_time_result']

    if len(current_run_result) == 2:
        run_time = np.absolute(current_run_result[0]['time_seq'] - current_run_result[1]['time_seq'])

    calc_obj = outlier()

    if "speed_index" in result_data:
        si_value = result_data['speed_index']
        psi_value = result_data['perceptual_speed_index']
    else:
        si_value = 0
        psi_value = 0
    run_time_dict = {'run_time': run_time, 'si': si_value, 'psi': psi_value}

    if test_method_name in result:
        result[test_method_name]['total_run_no'] += 1
        result[test_method_name]['total_time'] += run_time
        if run_time == 0:
            result[test_method_name]['error_no'] += 1
        else:
            result[test_method_name]['time_list'].append(run_time_dict)
        if run_time > result[test_method_name]['max_time']:
            result[test_method_name]['max_time'] = run_time
        if run_time < result[test_method_name]['min_time']:
            result[test_method_name]['min_time'] = run_time
        result[test_method_name]['detail'].extend(current_run_result)
        if len(result[test_method_name]['time_list']) >= outlier_check_point:
            result[test_method_name]['avg_time'], result[test_method_name]['med_time'],\
                result[test_method_name]['std_dev'], result[test_method_name]['time_list'],\
                tmp_outlier, si_value, psi_value = calc_obj.detect(result[test_method_name]['time_list'])
            result[test_method_name]['outlier'].extend(tmp_outlier)
    else:
        result[test_method_name] = {}
        result[test_method_name]['description'] = test_method_doc
        result[test_method_name]['total_run_no'] = 1
        result[test_method_name]['total_time'] = run_time
        result[test_method_name]['time_list'] = []
        result[test_method_name]['outlier'] = []
        if run_time == 0:
            result[test_method_name]['error_no'] = 1
            result[test_method_name]['max_time'] = 0
            result[test_method_name]['min_time'] = 0
        else:
            result[test_method_name]['error_no'] = 0
            result[test_method_name]['avg_time'] = run_time
            result[test_method_name]['med_time'] = run_time
            result[test_method_name]['max_time'] = run_time
            result[test_method_name]['min_time'] = run_time
            result[test_method_name]['time_list'].append(run_time_dict)
        result[test_method_name]['detail'] = current_run_result

    result[test_method_name]['video_fp'] = video_fp
    result[test_method_name]['web_app_name'] = web_app_name
    result[test_method_name]['speed_index'] = si_value
    result[test_method_name]['perceptual_speed_index'] = psi_value

    with open(output_fp, "wb") as fh:
        json.dump(result, fh, indent=2)

    # output sikuli status to static file
    with open(time_list_counter_fp, "r+") as fh:
        stat_data = json.load(fh)
        stat_data['time_list_counter'] = str(len(result[test_method_name]['time_list']))
        fh.seek(0)
        fh.write(json.dumps(stat_data))

def result_calculation(env, exec_timestamp_list, crop_data=None, calc_si=0):
    if os.path.exists(env.video_output_fp):
        fps = fps_cal(env.recording_log_fp)
        if fps != env.DEFAULT_VIDEO_RECORDING_FPS:
            result_data = None
            logger.warning(
                'Real FPS cannot reach default setting, ignore current result!, current FPS:[%s], default FPS:[%s]' % (
                str(fps), str(env.DEFAULT_VIDEO_RECORDING_FPS)))
        else:
            result_data = run_image_analyze(env.video_output_fp, env.img_output_dp, env.img_sample_dp, exec_timestamp_list, crop_data, fps, calc_si)
    else:
        result_data = None
    if result_data is not None:
        output_result(env.test_name, result_data, env.DEFAULT_TEST_RESULT, env.DEFAULT_STAT_RESULT, env.test_method_doc, env.DEFAULT_OUTLIER_CHECK_POINT, env.video_output_fp, env.web_app_name)


def fps_cal(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as fh:
            data = ''.join([line.replace('\n', '') for line in fh.readlines()])
            fps = map(int, re.findall('fps=(\s\d+\s)', data))
            count = Counter(fps)
        fh.close()
        return count.most_common()[0][0]
    else:
        return 0
