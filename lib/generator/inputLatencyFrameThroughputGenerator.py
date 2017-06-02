import json
import time
import copy
from baseGenerator import BaseGenerator
from inputLatencyAnimationDctGenerator import InputLatencyAnimationDctGenerator
from frameThroughputDctGenerator import FrameThroughputDctGenerator
from ..common.commonUtil import CommonUtil
from ..common.commonUtil import CalculationUtil
from ..common.logConfig import get_logger

logger = get_logger(__name__)


class InputLatencyFrameThroughputGenerator(BaseGenerator):

    BROWSER_VISUAL_EVENT_POINTS = {}

    def __init__(self, index_config, exec_config, online_config, global_config, input_env):
        super(InputLatencyFrameThroughputGenerator, self).__init__(index_config, exec_config, online_config,
                                                                   global_config, input_env)
        self.ft_generator = FrameThroughputDctGenerator(index_config, exec_config, online_config, global_config, input_env)
        self.il_generator = InputLatencyAnimationDctGenerator(index_config, exec_config, online_config, global_config, input_env)
        self.compare_result = {}

    def generate_update_result_for_combination(self, input_update_result, input_compare_result, input_run_time_dict):
        update_result = copy.deepcopy(input_update_result)
        update_result['total_run_no'] += 1
        update_result['detail'].extend(input_compare_result['running_time_result'])

        if input_compare_result['ft_run_time'] <= 0 or input_compare_result['il_run_time'] <= 0:
            update_result['error_no'] += 1
        else:
            update_result['time_list'].append(input_run_time_dict)

        update_result['video_fp'] = self.env.video_output_fp
        update_result['web_app_name'] = self.env.web_app_name
        update_result['revision'] = self.online_config['perfherder-revision']
        update_result['pkg_platform'] = self.online_config['perfherder-pkg-platform']

        for time_type in ['il_', 'ft_']:
            _, _, update_result[time_type + 'med_time'], update_result[time_type + 'avg_time'], \
                update_result[time_type + 'std_dev'], update_result[time_type + 'min_time'], \
                update_result[time_type + 'max_time'] = CalculationUtil.get_median_avg_sigma_value(
                    update_result['time_list'], time_type + 'run_time')

        update_result['video_fp'] = self.env.video_output_fp
        update_result['web_app_name'] = self.env.web_app_name
        update_result['revision'] = self.online_config['perfherder-revision']
        update_result['pkg_platform'] = self.online_config['perfherder-pkg-platform']
        return update_result

    def generate_sample_result(self, input_generator_name, input_sample_dict, input_sample_index):
        ft_return_result = self.ft_generator.generate_sample_result("FrameThroughputDctGenerator",
                                                                    input_sample_dict,
                                                                    input_sample_index)
        il_return_result = self.il_generator.generate_sample_result("InputLatencyAnimationDctGenerator",
                                                                    input_sample_dict,
                                                                    input_sample_index)
        ft_return_result.update(il_return_result)

        return ft_return_result

    def crop_images_based_on_samplefiles(self, input_data):
        ft_input_image_list = self.ft_generator.crop_images_based_on_samplefiles(input_data)
        il_input_image_list = self.il_generator.crop_images_based_on_samplefiles(input_data)
        ft_input_image_list.update(il_input_image_list)

        return ft_input_image_list

    def generate_result(self, input_data):
        il_compare_result = self.il_generator.generate_result(input_data)
        ft_compare_result = self.ft_generator.generate_result(input_data)

        running_time_result = []
        # get the real running_time_result for combination generator
        for item in il_compare_result['running_time_result']:
            if item['event'] == 'start':
                running_time_result.append(item)
                break
        for item in ft_compare_result['running_time_result']:
            if item['event'] == 'end':
                running_time_result.append(item)
                break

        # rename overlapped items and remove the original value
        for item in ['run_time', 'event_time_dict']:
            il_compare_result['il_' + item] = il_compare_result[item]
            ft_compare_result['ft_' + item] = ft_compare_result[item]
            del il_compare_result[item]
            del ft_compare_result[item]

        ft_compare_result.update(il_compare_result)
        ft_compare_result['running_time_result'] = running_time_result
        self.compare_result = ft_compare_result

        return self.compare_result

    def output_case_result(self, suite_upload_dp):

        if self.compare_result.get('ft_run_time', None) and self.compare_result.get('il_run_time', None):
            self.record_runtime_current_status(self.compare_result['ft_run_time'])

            history_result_data = CommonUtil.load_json_file(self.env.DEFAULT_TEST_RESULT)
            il_event_time_dict = self.compare_result.get('il_event_time_dict', {})
            ft_event_time_dict = self.compare_result.get('ft_event_time_dict', {})
            long_frame = self.compare_result.get('long_frame', 0)
            frame_throughput = self.compare_result.get('frame_throughput', 0)
            freeze_frames = self.compare_result.get('freeze_frames', 0)
            expected_frames = self.compare_result.get('expected_frames', 0)
            actual_paint_frames = self.compare_result.get('actual_paint_frames', 0)
            non_freeze_frame_timestamps = self.compare_result.get('non_freeze_frame_timestamps', 0)

            run_time_dict = {'ft_run_time': self.compare_result['ft_run_time'],
                             'il_run_time': self.compare_result['il_run_time'],
                             'folder': self.env.output_name,
                             'freeze_frames': freeze_frames,
                             'long_frame': long_frame,
                             'frame_throughput': frame_throughput,
                             'expected_frames': expected_frames,
                             'actual_paint_frames': actual_paint_frames,
                             'il_event_time': il_event_time_dict,
                             'ft_event_time': ft_event_time_dict,
                             'non_freeze_frame_timestamps': non_freeze_frame_timestamps}

            # init result dict if not exist
            init_result_dict = self.init_result_dict_variable(
                ['total_run_no', 'error_no'], ['time_list', 'detail'])
            update_result = history_result_data.get(self.env.test_name, init_result_dict)

            # based on current result add the data to different field
            history_result_data[self.env.test_name] = self.generate_update_result_for_combination(update_result, self.compare_result, run_time_dict)

            # write fps to history_result_data
            history_result_data['video-recording-fps'] = self.index_config['video-recording-fps']

            # dump to json file
            with open(self.env.DEFAULT_TEST_RESULT, "wb") as fh:
                json.dump(history_result_data, fh, indent=2)
            self.status_recorder.record_current_status({self.status_recorder.STATUS_TIME_LIST_COUNTER: str(len(history_result_data[self.env.test_name]['time_list']))})
        else:
            self.status_recorder.record_current_status({self.status_recorder.STATUS_IMG_COMPARE_RESULT: self.status_recorder.ERROR_COMPARE_RESULT_IS_NONE})

        # running time result was handled specially in this generator
        if self.exec_config['output-result-video-file']:
            start_time = time.time()
            self.output_runtime_result_video(self.compare_result['running_time_result'], suite_upload_dp)
            current_time = time.time()
            elapsed_time = current_time - start_time
            logger.debug("Generate Video Elapsed: [%s]" % elapsed_time)

        # clean up redundant image files
        self.clean_output_images(self.compare_result['running_time_result'], self.env.img_output_dp)
