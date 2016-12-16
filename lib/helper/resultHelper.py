import os
import re
import json
import time
import numpy as np
from collections import Counter
from ..common.outlier import outlier
from ..common.logConfig import get_logger
from ..common.imageTool import ImageTool
from ..common.commonUtil import CommonUtil
from ..common.videoFluency import VideoFluency

logger = get_logger(__name__)


def run_image_analyze(input_video_fp, output_img_dp, input_sample_dp, exec_timestamp_list, crop_data=None, fps=0, calc_si=0):
    return_result = {}
    if os.path.exists(output_img_dp) is False:
        os.mkdir(output_img_dp)
    img_tool_obj = ImageTool(fps=fps)
    start_time = time.time()
    img_tool_obj.convert_video_to_images(input_video_fp, output_img_dp, None, exec_timestamp_list)
    convert_video_to_images_end = time.time()
    elapsed_time = convert_video_to_images_end - start_time
    logger.debug("Convert Video to Image Time Elapsed: [%s]" % elapsed_time)
    if crop_data:
        img_tool_obj.crop_image(crop_data['target'], crop_data['output'], crop_data['range'])
        return_result['running_time_result'] = img_tool_obj.compare_with_sample_object(input_sample_dp)
    else:
        viewport = img_tool_obj.crop_viewport(input_sample_dp, output_img_dp)
        crop_viewport_end = time.time()
        elapsed_time = crop_viewport_end - convert_video_to_images_end
        logger.debug("Crop Viewport from All Images Elapsed: [%s]" % elapsed_time)

        img_tool_obj.crop_tab_view(input_sample_dp, output_img_dp, viewport)
        crop_tab_view_end = time.time()
        elapsed_time = crop_tab_view_end - crop_viewport_end
        logger.debug("Crop Tab_View from All Images Elapsed: [%s]" % elapsed_time)

        return_result['running_time_result'] = img_tool_obj.compare_with_sample_image_multi_process(input_sample_dp)
        end_time = time.time()
        elapsed_time = end_time - crop_viewport_end
        logger.debug("Compare Image Time Elapsed: [%s]" % elapsed_time)
    if calc_si == 1:
        start_time = time.time()
        si_progress = img_tool_obj.calculate_progress_for_si(return_result['running_time_result'])
        progress_end_time = time.time()
        elapsed_time = progress_end_time - start_time
        logger.debug("Calc Histogram Time Elapsed: [%s]" % elapsed_time)

        return_result['speed_index'] = img_tool_obj.calculate_speed_index(si_progress)
        calc_si_end_time = time.time()
        elapsed_time = calc_si_end_time - progress_end_time
        logger.debug("SI Integration Time Elapsed: [%s]" % elapsed_time)

        return_result['perceptual_speed_index'] = img_tool_obj.calculate_perceptual_speed_index(si_progress)
        end_time = time.time()
        elapsed_time = end_time - calc_si_end_time
        logger.debug("PSI Integration Time Elapsed: [%s]" % elapsed_time)
    return return_result


def output_result(test_method_name, result_data, output_fp, time_list_counter_fp, test_method_doc, outlier_check_point, video_fp, web_app_name, revision, pkg_platform):
    # result = {'class_name': {'total_run_no': 0, 'error_no': 0, 'total_time': 0, 'avg_time': 0, 'max_time': 0, 'min_time': 0, 'time_list':[] 'detail': []}}
    run_time = 0
    first_paint_time = 0
    if os.path.exists(output_fp):
        with open(output_fp) as fh:
            result = json.load(fh)
    else:
        result = {}

    current_run_result = result_data['running_time_result']

    if len(current_run_result) == 3:
        run_time = np.absolute(current_run_result[0]['time_seq'] - current_run_result[2]['time_seq'])
        first_paint_time = np.absolute(current_run_result[0]['time_seq'] - current_run_result[1]['time_seq'])

    calc_obj = outlier()

    if "speed_index" in result_data:
        si_value = result_data['speed_index']
        psi_value = result_data['perceptual_speed_index']
    else:
        si_value = 0
        psi_value = 0
    run_time_dict = {'run_time': run_time, 'si': si_value, 'psi': psi_value, 'first_paint_time': first_paint_time}

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
    result[test_method_name]['revision'] = revision
    result[test_method_name]['pkg_platform'] = pkg_platform

    with open(output_fp, "wb") as fh:
        json.dump(result, fh, indent=2)

    # output sikuli status to static file
    with open(time_list_counter_fp, "r+") as fh:
        stat_data = json.load(fh)
        stat_data['time_list_counter'] = str(len(result[test_method_name]['time_list']))
        fh.seek(0)
        fh.write(json.dumps(stat_data))


def output_waveform_info(result_data, waveform_fp, img_dp, video_fp):
    waveform_info = dict()
    waveform_info['video'] = video_fp
    current_run_result = result_data['running_time_result']
    if len(current_run_result) == 2:
        video_fluency_obj = VideoFluency()
        img_list = os.listdir(img_dp)
        img_list.sort(key=CommonUtil.natural_keys)
        start_fn = os.path.basename(current_run_result[0]['image_fp'])
        start_index = img_list.index(start_fn)
        end_fn = os.path.basename(current_run_result[1]['image_fp'])
        end_index = img_list.index(end_fn)
        for img_index in range(len(img_list)):
            img_list[img_index] = os.path.join(img_dp, img_list[img_index])
            if img_index < start_index or img_index > end_index:
                os.remove(img_list[img_index])
        waveform_info['data'], waveform_info['img_list'] = video_fluency_obj.frame_difference(img_dp)
        with open(waveform_fp, "wb") as fh:
            json.dump(waveform_info, fh, indent=2)


def result_calculation(env, exec_timestamp_list, crop_data=None, calc_si=0, waveform=0, revision="", pkg_platform=""):
    fps_stat = "1"
    if os.path.exists(env.video_output_fp):
        fps_stat, fps = fps_cal(env.recording_log_fp, env.DEFAULT_VIDEO_RECORDING_FPS)
        if int(fps_stat):
            result_data = None
            logger.warning('Real FPS cannot reach default setting, ignore current result!, current FPS:[%s], default FPS:[%s]' % (str(fps), str(env.DEFAULT_VIDEO_RECORDING_FPS)))
        else:
            result_data = run_image_analyze(env.video_output_fp, env.img_output_dp, env.img_sample_dp, exec_timestamp_list, crop_data, fps, calc_si)
    else:
        result_data = None

    # output sikuli status to static file
    with open(env.DEFAULT_STAT_RESULT, "r+") as fh:
        stat_data = json.load(fh)
        stat_data['fps_stat'] = fps_stat
        fh.seek(0)
        fh.write(json.dumps(stat_data))

    if result_data is not None:
        output_result(env.test_name, result_data, env.DEFAULT_TEST_RESULT, env.DEFAULT_STAT_RESULT, env.test_method_doc, env.DEFAULT_OUTLIER_CHECK_POINT, env.video_output_fp, env.web_app_name, revision, pkg_platform)
        if waveform == 1:
            output_waveform_info(result_data, env.waveform_fp, env.img_output_dp, env.video_output_fp)


def is_number_in_tolerance(number, default_fps, tolerance):
    return round(default_fps * (1 - tolerance)) <= number <= round(default_fps * (1 + tolerance))


def fps_cal(file_path, default_fps):
    status_success = '0'
    status_fail = '1'
    fps_stat = status_success
    fps_return = 0
    tolerance = 0.03  # recording fps tolerance is set to 3%
    fps_frequency_threshold = 0.9  # fps frequency should be more than 90%
    if os.path.exists(file_path):
        with open(file_path, 'r') as fh:
            data = ''.join([line.replace('\n', '') for line in fh.readlines()])
            fps = map(int, re.findall('fps=(\s\d+\s)', data))
            count = Counter(fps)
        fh.close()
        all_fps_tuple = count.most_common()
        if not all_fps_tuple:
            logger.error("Cannot get fps information from log.")
            fps_stat = status_fail
        else:
            # item[0]: fps
            # item[1]: counter
            total_record = sum([item[1] for item in all_fps_tuple])
            tolerance_fps_element = [item for item in all_fps_tuple if is_number_in_tolerance(item[0], default_fps, tolerance)]
            tolerance_fps_total_record = sum([item[1] for item in tolerance_fps_element])
            if float(tolerance_fps_total_record) / total_record >= fps_frequency_threshold:
                fps_return = sum([item[0] * item[1] for item in tolerance_fps_element]) / tolerance_fps_total_record
            else:
                fps_return = sum([item[0] * item[1] for item in all_fps_tuple]) / total_record
                fps_stat = status_fail
    else:
        logger.warning("Recording log doesn't exist.")
        fps_stat = status_fail
    return fps_stat, int(round(fps_return))
