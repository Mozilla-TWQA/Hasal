import os
import json
import time
import copy
import numpy as np
from baseGenerator import BaseGenerator
from frameThroughputDctGenerator import FrameThroughputDctGenerator
from ..helper.terminalHelper import find_terminal_view
from ..common.visualmetricsWrapper import find_tab_view
from ..common.visualmetricsWrapper import find_image_viewport
from ..common.imageUtil import generate_crop_data
from ..common.imageUtil import crop_images
from ..common.imageUtil import convert_to_dct
from ..common.imageUtil import find_browser_view
from ..common.imageUtil import compare_with_sample_image_multi_process
from ..common.imageUtil import CropRegion
from ..common.commonUtil import CommonUtil
from ..common.logConfig import get_logger

logger = get_logger(__name__)


class InputLatencyFrameThroughputGenerator(BaseGenerator):

    # We should not skip fraction when it comes to terminal region
    FULL_FRACTION = 1.0
    # It is used only when you want to get rid of status bar or panel on bottom left
    SKIP_STATUS_BAR_FRACTION = 0.95

    BROWSER_VISUAL_EVENT_POINTS = {
        # (IL start) <--- time ---> ( FT Start = IL end )
        'backward_search': [
            {'event': 'il_end', 'search_target': CropRegion.VIEWPORT, 'fraction': SKIP_STATUS_BAR_FRACTION, 'shift_result': True},
            {'event': 'il_start', 'search_target': CropRegion.TERMINAL, 'fraction': FULL_FRACTION, 'shift_result': True}
        ],
        # ( FT Start = IL end ) <--- time ---> (FT end)
        'forward_search': [
            {'event': 'ft_end', 'search_target': CropRegion.VIEWPORT, 'fraction': SKIP_STATUS_BAR_FRACTION, 'shift_result': True}
        ]
        # Note: We used to use 'start' and 'end' as events. However, in this generator, we use 2 sets of them.
        # il_start and il_end as 1 set and il_end and ft_end as another set.
    }

    @staticmethod
    def generate_sample_result(input_generator_name, input_sample_dict, input_sample_index):
        current_sample_data = copy.deepcopy(input_sample_dict)
        input_sample_data = current_sample_data[input_sample_index]
        sample_dct_obj = convert_to_dct(input_sample_data['fp'])
        return_result = {input_generator_name: {'dct': sample_dct_obj, 'crop_data': {}}}

        # crop sample data area
        # generate viewport crop area
        if CropRegion.VIEWPORT in input_sample_data:
            return_result[input_generator_name]['crop_data'][CropRegion.VIEWPORT] = input_sample_data[CropRegion.VIEWPORT]
            return_result[CropRegion.VIEWPORT] = input_sample_data[CropRegion.VIEWPORT]
        else:
            viewport_value = find_image_viewport(input_sample_data['fp'])
            return_result[input_generator_name]['crop_data'][CropRegion.VIEWPORT] = viewport_value
            return_result[CropRegion.VIEWPORT] = viewport_value

        # generate terminal crop area
        if CropRegion.TERMINAL in input_sample_data:
            # if already generated the data, reuse it.
            return_result[input_generator_name]['crop_data'][CropRegion.TERMINAL] = input_sample_data[CropRegion.TERMINAL]
        else:
            # TODO: we should replace the VIEWPORT location by BROWSER location in the future.
            # (Currently Mike implement the Win and Mac, no Linux)
            terminal_value = find_terminal_view(
                input_sample_data['fp'],
                return_result[input_generator_name]['crop_data'][CropRegion.VIEWPORT])
            return_result[input_generator_name]['crop_data'][CropRegion.TERMINAL] = terminal_value
            return_result[CropRegion.TERMINAL] = terminal_value

        # generate tab_view crop area
        if CropRegion.TAB_VIEW in input_sample_data:
            return_result[input_generator_name]['crop_data'][CropRegion.TAB_VIEW] = input_sample_data[CropRegion.TAB_VIEW]
        else:
            tabview_value = find_tab_view(input_sample_data['fp'], return_result[input_generator_name]['crop_data'][CropRegion.VIEWPORT])
            return_result[input_generator_name]['crop_data'][CropRegion.TAB_VIEW] = tabview_value
            return_result[CropRegion.TAB_VIEW] = tabview_value

        # generate browser crop area
        if CropRegion.BROWSER in input_sample_data:
            return_result[input_generator_name]['crop_data'][CropRegion.BROWSER] = input_sample_data[CropRegion.BROWSER]
        else:
            browser_view_value = find_browser_view(
                return_result[input_generator_name]['crop_data'][CropRegion.VIEWPORT],
                return_result[input_generator_name]['crop_data'][CropRegion.TAB_VIEW])
            return_result[input_generator_name]['crop_data'][CropRegion.BROWSER] = browser_view_value
            return_result[CropRegion.BROWSER] = browser_view_value

        # generate crop data
        if input_generator_name not in input_sample_dict[1]:
            crop_data_dict = generate_crop_data([input_sample_data], return_result[input_generator_name]['crop_data'])
        else:
            crop_data_dict = generate_crop_data([input_sample_data], input_sample_dict[1][input_generator_name]['crop_data'])

        # crop images
        crop_images(crop_data_dict)

        # tag event to sample
        return_result[input_generator_name]['event_tags'] = {}
        if input_sample_index == 1:
            for event_obj in InputLatencyFrameThroughputGenerator.BROWSER_VISUAL_EVENT_POINTS['backward_search']:
                search_target_fp = crop_data_dict[event_obj['search_target']]['fp_list'][0]['output_fp']
                return_result[input_generator_name]['event_tags'][event_obj['event']] = convert_to_dct(search_target_fp, event_obj['fraction'])
        elif input_sample_index == 2:
            for event_obj in InputLatencyFrameThroughputGenerator.BROWSER_VISUAL_EVENT_POINTS['forward_search']:
                search_target_fp = crop_data_dict[event_obj['search_target']]['fp_list'][0]['output_fp']
                return_result[input_generator_name]['event_tags'][event_obj['event']] = convert_to_dct(search_target_fp, event_obj['fraction'])

        return return_result

    def crop_images_based_on_samplefiles(self, input_data):
        """

        @param input_data:
        @return:
        """

        # compare source image list
        input_image_list = copy.deepcopy(input_data['converter_result'])

        # generate image list
        image_list = []
        for image_fn in input_data['converter_result']:
            image_list.append(input_data['converter_result'][image_fn])

        # generate crop data for all images
        crop_data_dict = generate_crop_data(image_list, input_data['sample_result'][1][self.__class__.__name__]['crop_data'])

        # crop images
        start_time = time.time()
        crop_images(crop_data_dict)
        last_end = time.time()
        elapsed_time = last_end - start_time
        logger.debug("Crop Image Time Elapsed: [%s]" % elapsed_time)

        # merge crop data and convert data
        for crop_target_name in crop_data_dict:
            for crop_img_obj in crop_data_dict[crop_target_name]['fp_list']:
                image_fn = os.path.basename(crop_img_obj['input_fp'])
                input_image_list[image_fn][crop_target_name] = crop_img_obj['output_fp']

        return input_image_list

    def generate_result(self, input_data):
        """

        @param input_data:
        @return:
        """

        self.compare_result = {}

        input_image_list = self.crop_images_based_on_samplefiles(input_data)
        self.compare_result['merged_crop_image_list'] = input_image_list

        # compare images
        compare_setting = {'default_fps': self.index_config['video-recording-fps'],
                           'event_points': self.BROWSER_VISUAL_EVENT_POINTS,
                           'generator_name': self.__class__.__name__,
                           'skip_status_bar_fraction': self.SKIP_STATUS_BAR_FRACTION,
                           'exec_timestamp_list': input_data['exec_timestamp_list'],
                           'threshold': self.index_config.get('compare-threshold', 0.0003),
                           'search_margin': self.index_config.get('search-margin', 10)}
        self.compare_result['running_time_result'] = compare_with_sample_image_multi_process(
            input_data['sample_result'],
            input_image_list,
            compare_setting)
        # get frame throughput values
        if self.compare_result.get('running_time_result', None):
            ft_run_time, ft_event_time_dict = self.calculate_runtime_base_on_event(
                self.compare_result['running_time_result'],
                'il_end', 'ft_end', self.index_config['video-recording-fps'])

            il_run_time, il_event_time_dict = self.calculate_runtime_base_on_event(
                self.compare_result['running_time_result'],
                'il_start', 'il_end', self.index_config['video-recording-fps'])

            self.compare_result.update({
                'ft_run_time': ft_run_time, 'ft_event_time_dict': ft_event_time_dict,
                'il_run_time': il_run_time, 'il_event_time_dict': il_event_time_dict}
            )

            self.compare_result.update(FrameThroughputDctGenerator.get_frame_throughput(
                                       self.compare_result['running_time_result'],
                                       self.compare_result['merged_crop_image_list'],
                                       'il_end', 'ft_end'))

        return self.compare_result

    @classmethod
    def calculate_runtime_base_on_event(cls, input_running_time_result, event_start, event_end, fps=90):
        """
        This customized method base on `baseGenerator.runtime_calculation_event_point_base`.
        However, when start and end at the same time, it will return the mid time between 0~1 frame, not 0 ms.

        For example, if FPS is 90, the running time of 1 frame is 11.11111 ms.
        When start and end at the same time, it will return 5.55555 ms ((1000 ms / 90 FPS) / 2).
        @param input_running_time_result: the running_time_result after do comparison.
            ex:
            [
                {'event': 'start', 'file': 'foo/bar/9487.bmp', 'time_seq': 5487.9487},
                {'event': 'end', 'file': 'foo/bar/9527.bmp', 'time_seq': 5566.5566}, ...
            ]
        @param fps: the current FPS. Default=90.
        @return: (running time, the dict of all events' time sequence).
        """
        run_time = -1
        event_time_dict = dict()

        start_event = cls.get_event_data_in_result_list(input_running_time_result,
                                                        event_start)
        end_event = cls.get_event_data_in_result_list(input_running_time_result,
                                                      event_end)
        if start_event and end_event:
            run_time = end_event.get('time_seq') - start_event.get('time_seq')
            event_time_dict[cls.EVENT_START] = 0
            event_time_dict[cls.EVENT_END] = run_time

            # when start and end at the same time, it will return the mid time between 0~1 frame, not 0 ms.
            if run_time == 0:
                run_time = 1000.0 / fps / 2

            if run_time > 0:
                for custom_event in input_running_time_result:
                    custom_event_name = custom_event.get('event')
                    if custom_event_name != cls.EVENT_START \
                            and custom_event_name != cls.EVENT_END:
                        event_time_dict[custom_event_name] = np.absolute(
                            custom_event.get('time_seq') - start_event.get('time_seq'))

        return run_time, event_time_dict

    def output_case_result(self, suite_upload_dp):

        if self.compare_result.get('ft_run_time', None) and self.compare_result.get('il_run_time', None):
            self.record_runtime_current_status(self.compare_result['ft_run_time'])

            history_result_data = CommonUtil.load_json_file(self.env.DEFAULT_TEST_RESULT)
            event_time_dict = self.compare_result.get('event_time_dict', {})
            long_frame = self.compare_result.get('long_frame', 0)
            frame_throughput = self.compare_result.get('frame_throughput', 0)
            freeze_frames = self.compare_result.get('freeze_frames', 0)
            expected_frames = self.compare_result.get('expected_frames', 0)
            actual_paint_frames = self.compare_result.get('actual_paint_frames', 0)

            run_time_dict = {'ft_run_time': self.compare_result['ft_run_time'],
                             'il_run_time': self.compare_result['il_run_time'],
                             'folder': self.env.output_name,
                             'freeze_frames': freeze_frames,
                             'long_frame': long_frame,
                             'frame_throughput': frame_throughput,
                             'expected_frames': expected_frames,
                             'actual_paint_frames': actual_paint_frames,
                             'event_time': event_time_dict}

            # init result dict if not exist
            init_result_dict = self.init_result_dict_variable(
                ['total_run_no', 'error_no'], ['time_list', 'detail'])
            update_result = history_result_data.get(self.env.test_name, init_result_dict)

            # based on current result add the data to different field
            history_result_data[self.env.test_name] = self.generate_update_result_for_combination(
                                                                   update_result, self.compare_result, run_time_dict)

            # dump to json file
            with open(self.env.DEFAULT_TEST_RESULT, "wb") as fh:
                json.dump(history_result_data, fh, indent=2)
            self.status_recorder.record_current_status({self.status_recorder.STATUS_TIME_LIST_COUNTER: str(len(history_result_data[self.env.test_name]['time_list']))})
        else:
            self.status_recorder.record_current_status({self.status_recorder.STATUS_IMG_COMPARE_RESULT: self.status_recorder.ERROR_COMPARE_RESULT_IS_NONE})

        if self.exec_config['output-result-video-file']:
            start_time = time.time()
            self.output_runtime_result_video(self.compare_result['running_time_result'], suite_upload_dp)
            current_time = time.time()
            elapsed_time = current_time - start_time
            logger.debug("Generate Video Elapsed: [%s]" % elapsed_time)
