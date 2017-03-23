import os
import time
import copy
from ..common.imageUtil import generate_crop_data
from ..common.imageUtil import crop_images
from ..common.imageUtil import convert_to_dct
from ..common.imageUtil import compare_with_sample_image_multi_process
from ..common.visualmetricsWrapper import find_image_viewport
from ..common.logConfig import get_logger

logger = get_logger(__name__)


class DctAnimationInputLatencyGenerator(object):

    SEARCH_TARGET_VIEWPORT = 'viewport'
    SEARCH_TARGET_ORIGINAL = 'original'
    SKIP_STATUS_BAR_FRACTION = 1.0

    BROWSER_VISUAL_EVENT_POINTS = {
        'backward_search': [{'event': 'end', 'search_target': SEARCH_TARGET_VIEWPORT, 'fraction': SKIP_STATUS_BAR_FRACTION, 'shift_result': True},
                            {'event': 'start', 'search_target': SEARCH_TARGET_ORIGINAL, 'fraction': SKIP_STATUS_BAR_FRACTION, 'shift_result': True}]
    }

    @staticmethod
    def generate_sample_result(input_generator_name, input_sample_dict, input_sample_index):
        current_sample_data = copy.deepcopy(input_sample_dict)
        input_sample_data = current_sample_data[input_sample_index]
        sample_dct_obj = convert_to_dct(input_sample_data['fp'])
        return_result = {input_generator_name: {'dct': sample_dct_obj, 'crop_data': {}}}

        # crop sample data area
        # generate viewport crop area
        if DctAnimationInputLatencyGenerator.SEARCH_TARGET_VIEWPORT in input_sample_data:
            return_result[input_generator_name]['crop_data'][DctAnimationInputLatencyGenerator.SEARCH_TARGET_VIEWPORT] = input_sample_data[DctAnimationInputLatencyGenerator.SEARCH_TARGET_VIEWPORT]
        else:
            viewport_value = find_image_viewport(input_sample_data['fp'])
            return_result[input_generator_name]['crop_data'][DctAnimationInputLatencyGenerator.SEARCH_TARGET_VIEWPORT] = viewport_value
            return_result[DctAnimationInputLatencyGenerator.SEARCH_TARGET_VIEWPORT] = viewport_value

        # generate crop data
        if input_generator_name not in input_sample_dict[1]:
            crop_data_dict = generate_crop_data([input_sample_data], return_result[input_generator_name]['crop_data'])
        else:
            crop_data_dict = generate_crop_data([input_sample_data], input_sample_dict[1][input_generator_name]['crop_data'])

        # crop images
        crop_images(crop_data_dict)

        if input_sample_index == 1:
            return_result[input_generator_name]['event_tags'] = {}
        elif input_sample_index == 2:
            # tag event to sample
            return_result[input_generator_name]['event_tags'] = {}
            for event_obj in DctAnimationInputLatencyGenerator.BROWSER_VISUAL_EVENT_POINTS['backward_search']:
                if event_obj['search_target'] == DctAnimationInputLatencyGenerator.SEARCH_TARGET_ORIGINAL:
                    return_result[input_generator_name]['event_tags'][event_obj['event']] = sample_dct_obj
                else:
                    search_target_fp = crop_data_dict[event_obj['search_target']]['fp_list'][0]['output_fp']
                    return_result[input_generator_name]['event_tags'][event_obj['event']] = convert_to_dct(search_target_fp, event_obj['fraction'])

        return return_result

    def crop_images_based_on_samplefiles(self, input_data):
        # compare source image list
        input_image_list = copy.deepcopy(input_data['converter_result'])

        # generate image list
        image_list = []
        for image_fn in input_data['converter_result']:
            image_list.append(input_data['converter_result'][image_fn])

        # generate crop data for all images
        crop_data_dict = generate_crop_data(image_list,
                                            input_data['sample_result'][1][self.__class__.__name__]['crop_data'])

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

        # merge crop data and convert data
        for image_fn in input_image_list:
            input_image_list[image_fn][self.SEARCH_TARGET_ORIGINAL] = input_image_list[image_fn]['fp']

        return input_image_list

    def generate_result(self, input_data, input_global_result):
        """

        @param input_data:
        @return:
        """
        compare_result = {}

        input_image_list = self.crop_images_based_on_samplefiles(input_data)
        compare_result['merged_crop_image_list'] = input_image_list

        # TODO: the threshold on Windows and Ubuntu are different.
        diff_threshold = 0.005
        import sys
        if sys.platform == 'linux2':
            diff_threshold = 0.01

        compare_setting = {
            'default_fps': input_data['default_fps'],
            'event_points': self.BROWSER_VISUAL_EVENT_POINTS,
            'generator_name': self.__class__.__name__,
            'skip_status_bar_fraction': self.SKIP_STATUS_BAR_FRACTION,
            'exec_timestamp_list': input_data['exec_timestamp_list'],
            'threshold': diff_threshold,
            'search_margin': 1
        }
        compare_result['running_time_result'] = compare_with_sample_image_multi_process(input_data['sample_result'],
                                                                                        input_image_list,
                                                                                        compare_setting)

        return compare_result
