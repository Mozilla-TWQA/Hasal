import os
import time
import copy
import numpy as np
from ..common.imageUtil import generate_crop_data
from ..common.imageUtil import crop_images
from ..common.imageUtil import convert_to_dct
from ..common.visualmetricsWrapper import find_tab_view
from ..common.imageUtil import find_browser_view
from ..common.imageUtil import compare_with_sample_image_multi_process
from ..common.visualmetricsWrapper import find_image_viewport
from ..common.commonUtil import CommonUtil
from ..common.logConfig import get_logger

logger = get_logger(__name__)


class FrameThroughputDctGenerator(object):

    SEARCH_TARGET_VIEWPORT = 'viewport'
    SEARCH_TARGET_TAB_VIEW = 'tab_view'
    SEARCH_TARGET_BROWSER = 'browser'
    SKIP_STATUS_BAR_FRACTION = 0.95
    DEFAULT_CROP_TARGET_LIST = [SEARCH_TARGET_VIEWPORT, SEARCH_TARGET_TAB_VIEW, SEARCH_TARGET_BROWSER]

    BROWSER_VISUAL_EVENT_POINTS = {
        'backward_search': [{'event': 'start', 'search_target': SEARCH_TARGET_VIEWPORT, 'fraction': 1.0}],
        'forward_search': [{'event': 'end', 'search_target': SEARCH_TARGET_VIEWPORT, 'fraction': 1.0}]}

    def get_frame_throughput(self, result_list, input_image_list):
        """

        @param result_list:
        @param input_image_list:
        @return:
        """

        return_result = dict()
        try:
            image_fn_list = copy.deepcopy(input_image_list.keys())
            image_fn_list.sort(key=CommonUtil.natural_keys)

            # get start point and end point from input data
            start_event_fp = None
            end_event_fp = None
            for result in result_list:
                if 'start' in result:
                    start_event_fp = result['start']
                if 'end' in result:
                    end_event_fp = result['end']
            if not start_event_fp or not end_event_fp:
                raise Exception('[ERROR] Cannot find either start point or end point!')
            else:
                start_event_fn = os.path.basename(start_event_fp)
                start_event_index = image_fn_list.index(start_event_fn)
                end_event_fn = os.path.basename(end_event_fp)
                end_event_index = image_fn_list.index(end_event_fn)

            # calculate viewport variations between start point and end point
            # based on variation to determine if frame is freeze and result in frame throughput related values
            start_target_fp = input_image_list[image_fn_list[start_event_index]][self.SEARCH_TARGET_VIEWPORT]
            start_target_time_seq = input_image_list[image_fn_list[start_event_index]]['time_seq']
            img_list_dct = [convert_to_dct(start_target_fp)]
            weight, height = img_list_dct[-1].shape

            freeze_count = 0
            base_time_seq = start_target_time_seq
            frame_throughput_time_seq = [start_target_time_seq]
            long_frame_time_seq = []
            for img_index in range(start_event_index + 1, end_event_index + 1):
                image_fn = image_fn_list[img_index]
                image_data = copy.deepcopy(input_image_list[image_fn])
                img_list_dct.append(convert_to_dct(image_data[self.SEARCH_TARGET_VIEWPORT]))
                mismatch_rate = np.sum(np.absolute(np.subtract(img_list_dct[-2], img_list_dct[-1]))) / (weight * height)
                if not mismatch_rate:
                    freeze_count += 1
                    logger.debug("Image freeze from previous frame: %s", image_fn)
                else:
                    current_long_frame = image_data['time_seq'] - base_time_seq
                    frame_throughput_time_seq.append(image_data['time_seq'])
                    long_frame_time_seq.append(current_long_frame)
                    base_time_seq = image_data['time_seq']

            long_frame = max(long_frame_time_seq)
            expected_frames = end_event_index - start_event_index + 1
            actual_paint_frames = expected_frames - freeze_count
            frame_throughput = float(actual_paint_frames) / expected_frames

            return_result = dict()
            return_result['long_frame'] = long_frame
            return_result['frame_throughput'] = frame_throughput
            return_result['freeze_frames'] = freeze_count
            return_result['expected_frames'] = expected_frames
            return_result['actual_paint_frames'] = actual_paint_frames
            return_result['time_sequence'] = frame_throughput_time_seq

        except Exception as e:
            logger.error(e)

        return return_result

    @staticmethod
    def generate_sample_result(input_generator_name, input_sample_dict, input_sample_index):
        current_sample_data = copy.deepcopy(input_sample_dict)
        input_sample_data = current_sample_data[input_sample_index]
        sample_dct_obj = convert_to_dct(input_sample_data['fp'])
        return_result = {input_generator_name: {'dct': sample_dct_obj, 'crop_data': {}}}

        # crop sample data area
        # generate viewport crop area
        if FrameThroughputDctGenerator.SEARCH_TARGET_VIEWPORT in input_sample_data:
            return_result[input_generator_name]['crop_data'][FrameThroughputDctGenerator.SEARCH_TARGET_VIEWPORT] = input_sample_data[FrameThroughputDctGenerator.SEARCH_TARGET_VIEWPORT]
            return_result[FrameThroughputDctGenerator.SEARCH_TARGET_VIEWPORT] = input_sample_data[FrameThroughputDctGenerator.SEARCH_TARGET_VIEWPORT]
        else:
            viewport_value = find_image_viewport(input_sample_data['fp'])
            return_result[input_generator_name]['crop_data'][FrameThroughputDctGenerator.SEARCH_TARGET_VIEWPORT] = viewport_value
            return_result[FrameThroughputDctGenerator.SEARCH_TARGET_VIEWPORT] = viewport_value

        # generate tab_view crop area
        if FrameThroughputDctGenerator.SEARCH_TARGET_TAB_VIEW in input_sample_data:
            return_result[input_generator_name]['crop_data'][FrameThroughputDctGenerator.SEARCH_TARGET_TAB_VIEW] = input_sample_data[FrameThroughputDctGenerator.SEARCH_TARGET_TAB_VIEW]
        else:
            tabview_value = find_tab_view(input_sample_data['fp'], return_result[input_generator_name]['crop_data'][
                FrameThroughputDctGenerator.SEARCH_TARGET_VIEWPORT])
            return_result[input_generator_name]['crop_data'][FrameThroughputDctGenerator.SEARCH_TARGET_TAB_VIEW] = tabview_value
            return_result[FrameThroughputDctGenerator.SEARCH_TARGET_TAB_VIEW] = tabview_value

        # generate browser crop area
        if FrameThroughputDctGenerator.SEARCH_TARGET_BROWSER in input_sample_data:
            return_result[input_generator_name]['crop_data'][FrameThroughputDctGenerator.SEARCH_TARGET_BROWSER] = input_sample_data[FrameThroughputDctGenerator.SEARCH_TARGET_BROWSER]
        else:
            browser_view_value = find_browser_view(
                return_result[input_generator_name]['crop_data'][FrameThroughputDctGenerator.SEARCH_TARGET_VIEWPORT],
                return_result[input_generator_name]['crop_data'][FrameThroughputDctGenerator.SEARCH_TARGET_TAB_VIEW])
            return_result[input_generator_name]['crop_data'][FrameThroughputDctGenerator.SEARCH_TARGET_BROWSER] = browser_view_value
            return_result[FrameThroughputDctGenerator.SEARCH_TARGET_BROWSER] = browser_view_value

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
            for event_obj in FrameThroughputDctGenerator.BROWSER_VISUAL_EVENT_POINTS['backward_search']:
                search_target_fp = crop_data_dict[event_obj['search_target']]['fp_list'][0]['output_fp']
                return_result[input_generator_name]['event_tags'][event_obj['event']] = convert_to_dct(search_target_fp, event_obj['fraction'])
        elif input_sample_index == 2:
            for event_obj in FrameThroughputDctGenerator.BROWSER_VISUAL_EVENT_POINTS['forward_search']:
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

    def generate_result(self, input_data, input_global_result):
        """

        @param input_data:
        @return:
        """

        compare_result = {}

        input_image_list = self.crop_images_based_on_samplefiles(input_data)
        compare_result['merged_crop_image_list'] = input_image_list

        # compare images
        compare_setting = {'default_fps': input_data['index_config']['video-recording-fps'], 'event_points': self.BROWSER_VISUAL_EVENT_POINTS,
                           'generator_name': self.__class__.__name__,
                           'skip_status_bar_fraction': self.SKIP_STATUS_BAR_FRACTION,
                           'exec_timestamp_list': input_data['exec_timestamp_list'],
                           'threshold': input_data['index_config']['compare-threshold'],
                           'search_margin': input_data['index_config']['search-margin']}
        compare_result['running_time_result'] = compare_with_sample_image_multi_process(input_data['sample_result'],
                                                                                        input_image_list,
                                                                                        compare_setting)
        # get frame throughput values
        compare_result.update(
            self.get_frame_throughput(compare_result['running_time_result'], compare_result['merged_crop_image_list']))

        return compare_result
