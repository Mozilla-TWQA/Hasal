import os
import re
import json
import time
import shutil
import tempfile
import numpy as np
from collections import Counter
from ..common.outlier import outlier
from ..common.logConfig import get_logger
from ..common.imageTool import ImageTool
from ..common.commonUtil import CommonUtil
from ..common.videoFluency import VideoFluency
from ..common.environment import Environment
from multiprocessing import Process

logger = get_logger(__name__)


def run_image_analyze(input_video_fp, output_img_dp, input_sample_dp, crop_data=None, fps=0, calc_si=0):
    return_result = {}
    if os.path.exists(output_img_dp) is False:
        os.mkdir(output_img_dp)
    img_tool_obj = ImageTool(fps=fps)
    start_time = time.time()
    img_tool_obj.convert_video_to_images(input_video_fp, output_img_dp, None)
    last_end = time.time()
    elapsed_time = last_end - start_time
    logger.debug("Convert Video to Image Time Elapsed: [%s]" % elapsed_time)
    if crop_data:
        img_tool_obj.crop_image(crop_data['target'], crop_data['output'], crop_data['range'])
        return_result['running_time_result'] = img_tool_obj.compare_with_sample_object(input_sample_dp)
    else:
        sample_fp_list = img_tool_obj.get_sample_img_list(input_sample_dp)
        viewport = img_tool_obj.find_image_viewport(sample_fp_list[0])
        tab_view = img_tool_obj.find_tab_view(sample_fp_list[0], viewport)
        browser_view = img_tool_obj.find_browser_view(viewport, tab_view)
        target_region = {
            Environment.SEARCH_TARGET_VIEWPORT: viewport,
            Environment.SEARCH_TARGET_TAB_VIEW: tab_view,
            Environment.SEARCH_TARGET_BROWSER: browser_view
        }

        # multi-processing to crop different regions from original images
        p_list = []
        for region in target_region.keys():
            args = [input_sample_dp, output_img_dp, region, target_region[region]]
            p_list.append(Process(target=img_tool_obj.crop_target_region, args=args))
            p_list[-1].start()
        for p in p_list:
            p.join()
        current_time = time.time()
        elapsed_time = current_time - last_end
        logger.debug("Crop All Regions Elapsed: [%s]" % elapsed_time)
        last_end = current_time

        return_result['running_time_result'] = img_tool_obj.compare_with_sample_image_multi_process(input_sample_dp)
        end_time = time.time()
        elapsed_time = end_time - last_end
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


def output_result(test_method_name, result_data, output_fp, time_list_counter_fp, test_method_doc, outlier_check_point, video_fp, web_app_name, revision, pkg_platform, test_output):
    # result = {'class_name': {'total_run_no': 0, 'error_no': 0, 'total_time': 0, 'avg_time': 0, 'max_time': 0, 'min_time': 0, 'time_list':[] 'detail': []}}
    if os.path.exists(output_fp):
        with open(output_fp) as fh:
            result = json.load(fh)
    else:
        result = {}

    current_run_result = result_data['running_time_result']

    start_time = 0
    end_time = 0
    for event_data in current_run_result:
        if 'start' in event_data:
            start_time = event_data['time_seq']
        if 'end' in event_data:
            end_time = event_data['time_seq']
    run_time = end_time - start_time

    event_time_dict = dict()
    for event_data in current_run_result:
        for event_name in event_data:
            if event_name != 'time_seq' and event_name != 'start' and event_name != 'end':
                event_time_dict[event_name] = np.absolute(event_data['time_seq'] - start_time)

    calc_obj = outlier()
    if "speed_index" in result_data:
        si_value = result_data['speed_index']
        psi_value = result_data['perceptual_speed_index']
    else:
        si_value = 0
        psi_value = 0
    run_time_dict = {'run_time': run_time, 'si': si_value, 'psi': psi_value, 'folder': test_output}
    run_time_dict.update(event_time_dict)

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
            result[test_method_name]['min_time'] = result[test_method_name]['time_list'][0]['run_time']
            result[test_method_name]['max_time'] = result[test_method_name]['time_list'][-1]['run_time']
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


def output_video(result_data, video_fp):
    start_fp = None
    end_fp = None
    current_run_result = result_data['running_time_result']
    for event_data in current_run_result:
        if 'start' in event_data:
            start_fp = event_data['start']
        if 'end' in event_data:
            end_fp = event_data['end']
    if not start_fp and not end_fp:
        return None
    else:
        source_dp = os.path.join(os.path.dirname(start_fp), Environment.SEARCH_TARGET_BROWSER)
        img_list = os.listdir(source_dp)
        img_list.sort(key=CommonUtil.natural_keys)
        start_fn = os.path.basename(start_fp)
        end_fn = os.path.basename(end_fp)
        file_ext = os.path.splitext(start_fn)[1]
        extended_range = Environment.DEFAULT_VIDEO_RECORDING_FPS
        start_index = max(0, img_list.index(start_fn) - extended_range)
        end_index = min(len(img_list) - 1, img_list.index(end_fn) + extended_range)
        tempdir = tempfile.mkdtemp()
        count = 0
        for img_index in range(start_index, end_index + 1):
            imf_fp = os.path.join(source_dp, img_list[img_index])
            new_img_fp = os.path.join(tempdir, '{0:05d}'.format(count) + file_ext)
            shutil.copyfile(imf_fp, new_img_fp)
            count += 1

    codec = "ffmpeg"
    source = " -i " + os.path.join(tempdir, "%05d" + file_ext)
    fps = " -r " + str(Environment.DEFAULT_VIDEO_RECORDING_FPS)
    video_format = " -pix_fmt yuv420p"
    video_out = " " + video_fp
    command = codec + source + fps + video_format + video_out
    os.system(command)
    shutil.rmtree(tempdir)


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


def result_calculation(env, crop_data=None, calc_si=0, waveform=0, revision="", pkg_platform="", suite_upload_dp=""):
    fps_stat = "1"
    if os.path.exists(env.video_output_fp):
        fps_stat, fps = fps_cal(env.recording_log_fp, env.DEFAULT_VIDEO_RECORDING_FPS)
        if int(fps_stat):
            result_data = None
            logger.warning('Real FPS cannot reach default setting, ignore current result!, current FPS:[%s], default FPS:[%s]' % (str(fps), str(env.DEFAULT_VIDEO_RECORDING_FPS)))
        else:
            result_data = run_image_analyze(env.video_output_fp, env.img_output_dp, env.img_sample_dp, crop_data, fps, calc_si)
    else:
        result_data = None

    # output sikuli status to static file
    with open(env.DEFAULT_STAT_RESULT, "r+") as fh:
        stat_data = json.load(fh)
        stat_data['fps_stat'] = fps_stat
        fh.seek(0)
        fh.write(json.dumps(stat_data))

    if result_data is not None:
        output_result(env.test_name, result_data, env.DEFAULT_TEST_RESULT, env.DEFAULT_STAT_RESULT, env.test_method_doc, env.DEFAULT_OUTLIER_CHECK_POINT, env.video_output_fp, env.web_app_name, revision, pkg_platform, env.output_name)
        start_time = time.time()
        output_video(result_data, env.converted_video_output_fp)
        current_time = time.time()
        elapsed_time = current_time - start_time
        logger.debug("Generate Video Elapsed: [%s]" % elapsed_time)
        if waveform == 1:
            output_waveform_info(result_data, env.waveform_fp, env.img_output_dp, env.video_output_fp)

        upload_case_name = "_".join(env.output_name.split("_")[2:-1])
        upload_case_dp = os.path.join(suite_upload_dp, upload_case_name)
        if os.path.exists(upload_case_dp) is False:
            os.mkdir(upload_case_dp)
        shutil.move(env.converted_video_output_fp, upload_case_dp)


def is_number_in_tolerance(number, default_fps, tolerance):
    return int(default_fps * (1 - tolerance)) <= number <= round(default_fps * (1 + tolerance))


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
