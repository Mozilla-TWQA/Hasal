import copy
from ..common.imageUtil import convert_to_dct
from ..common.imageUtil import compare_with_sample_image_multi_process
from ..common.logConfig import get_logger

logger = get_logger(__name__)


class DctInputLatencyGenerator(object):

    SEARCH_TARGET_ORIGINAL = 'original'
    SKIP_STATUS_BAR_FRACTION = 1.0

    BROWSER_VISUAL_EVENT_POINTS = {
        'backward_search': [{'event': 'start', 'search_target': SEARCH_TARGET_ORIGINAL, 'fraction': 1.0, 'shift_result': True}],
        'forward_search': [{'event': 'end', 'search_target': SEARCH_TARGET_ORIGINAL, 'fraction': 1.0, 'shift_result': False}]}

    @staticmethod
    def generate_sample_result(input_generator_name, input_sample_dict, input_sample_index):
        current_sample_data = copy.deepcopy(input_sample_dict)
        input_sample_data = current_sample_data[input_sample_index]
        sample_dct_obj = convert_to_dct(input_sample_data['fp'])
        return_result = {input_generator_name: {'dct': sample_dct_obj, 'crop_data': {}}}

        # tag event to sample
        return_result[input_generator_name]['event_tags'] = {}
        if input_sample_index == 1:
            for event_obj in DctInputLatencyGenerator.BROWSER_VISUAL_EVENT_POINTS['backward_search']:
                return_result[input_generator_name]['event_tags'][event_obj['event']] = sample_dct_obj
        elif input_sample_index == 2:
            for event_obj in DctInputLatencyGenerator.BROWSER_VISUAL_EVENT_POINTS['forward_search']:
                return_result[input_generator_name]['event_tags'][event_obj['event']] = sample_dct_obj
        return return_result

    def generate_result(self, input_data, input_global_result):
        """

        @param input_data:
        @return:
        """
        compare_result = {}

        # compare source image list
        input_image_list = copy.deepcopy(input_data['converter_result'])

        # generate image list
        image_list = []
        for image_fn in input_data['converter_result']:
            image_list.append(input_data['converter_result'][image_fn])

        # merge crop data and convert data
        for image_fn in input_image_list:
            input_image_list[image_fn][self.SEARCH_TARGET_ORIGINAL] = input_image_list[image_fn]['fp']

        # compare images
        compare_setting = {'default_fps': input_data['default_fps'], 'event_points': self.BROWSER_VISUAL_EVENT_POINTS,
                           'generator_name': self.__class__.__name__, 'skip_status_bar_fraction': self.SKIP_STATUS_BAR_FRACTION,
                           'exec_timestamp_list': input_data['exec_timestamp_list'], 'threshold': 0.005, 'search_margin': 1}
        compare_result['running_time_result'] = compare_with_sample_image_multi_process(input_data['sample_result'], input_image_list, compare_setting)

        return compare_result
