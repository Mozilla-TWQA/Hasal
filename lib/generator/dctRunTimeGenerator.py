import os
import time
import copy
from ..common.imageUtil import generate_crop_data
from ..common.imageUtil import crop_images
from ..common.imageUtil import convert_to_dct
from ..common.imageUtil import find_tab_view
from ..common.imageUtil import find_browser_view
from ..common.imageUtil import compare_with_sample_image_multi_process
from ..thirdparty.visualmetrics import find_image_viewport
from ..common.logConfig import get_logger

logger = get_logger(__name__)


class DctRunTimeGenerator(object):

    SEARCH_TARGET_VIEWPORT = 'viewport'
    SEARCH_TARGET_TAB_VIEW = 'tab_view'
    SEARCH_TARGET_BROWSER = 'browser'
    SKIP_STATUS_BAR_FRACTION = 0.95
    DEFAULT_CROP_TARGET_LIST = [SEARCH_TARGET_VIEWPORT, SEARCH_TARGET_TAB_VIEW, SEARCH_TARGET_BROWSER]

    BROWSER_VISUAL_EVENT_POINTS = {
        'backward_search': [{'event': 'first_paint', 'search_target': SEARCH_TARGET_VIEWPORT, 'fraction': SKIP_STATUS_BAR_FRACTION},
                            {'event': 'start', 'search_target': SEARCH_TARGET_TAB_VIEW, 'fraction': 1.0}],
        'forward_search': [
            {'event': 'viewport_visual_complete', 'search_target': SEARCH_TARGET_VIEWPORT, 'fraction': 1.0},
            {'event': 'end', 'search_target': SEARCH_TARGET_BROWSER, 'fraction': 1.0}]}

    @staticmethod
    def generate_sample_result(input_generator_name, input_sample_dict, input_sample_index):
        current_sample_data = copy.deepcopy(input_sample_dict)
        input_sample_data = current_sample_data[input_sample_index]
        sample_dct_obj = convert_to_dct(input_sample_data['fp'])
        return_result = {input_generator_name: {'dct': sample_dct_obj, 'crop_data': {}}}

        # crop sample data area
        # generate viewport crop area
        if DctRunTimeGenerator.SEARCH_TARGET_VIEWPORT in input_sample_data:
            return_result[input_generator_name]['crop_data'][DctRunTimeGenerator.SEARCH_TARGET_VIEWPORT] = \
            input_sample_data[DctRunTimeGenerator.SEARCH_TARGET_VIEWPORT]
        else:
            viewport_value = find_image_viewport(input_sample_data['fp'])
            return_result[input_generator_name]['crop_data'][DctRunTimeGenerator.SEARCH_TARGET_VIEWPORT] = viewport_value
            return_result[DctRunTimeGenerator.SEARCH_TARGET_VIEWPORT] = viewport_value

        # generate tab_view crop area
        if DctRunTimeGenerator.SEARCH_TARGET_TAB_VIEW in input_sample_data:
            return_result[input_generator_name]['crop_data'][DctRunTimeGenerator.SEARCH_TARGET_TAB_VIEW] = \
            input_sample_data[DctRunTimeGenerator.SEARCH_TARGET_TAB_VIEW]
        else:
            tabview_value = find_tab_view(input_sample_data['fp'], return_result[input_generator_name]['crop_data'][
                DctRunTimeGenerator.SEARCH_TARGET_VIEWPORT])
            return_result[input_generator_name]['crop_data'][DctRunTimeGenerator.SEARCH_TARGET_TAB_VIEW] = tabview_value
            return_result[DctRunTimeGenerator.SEARCH_TARGET_TAB_VIEW] = tabview_value

        # generate browser crop area
        if DctRunTimeGenerator.SEARCH_TARGET_BROWSER in input_sample_data:
            return_result[input_generator_name]['crop_data'][DctRunTimeGenerator.SEARCH_TARGET_BROWSER] = \
            input_sample_data[DctRunTimeGenerator.SEARCH_TARGET_BROWSER]
        else:
            browser_view_value = find_browser_view(
                return_result[input_generator_name]['crop_data'][DctRunTimeGenerator.SEARCH_TARGET_VIEWPORT],
                return_result[input_generator_name]['crop_data'][DctRunTimeGenerator.SEARCH_TARGET_TAB_VIEW])
            return_result[input_generator_name]['crop_data'][DctRunTimeGenerator.SEARCH_TARGET_BROWSER] = browser_view_value
            return_result[DctRunTimeGenerator.SEARCH_TARGET_BROWSER] = browser_view_value

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
            for event_obj in DctRunTimeGenerator.BROWSER_VISUAL_EVENT_POINTS['backward_search']:
                search_target_fp = crop_data_dict[event_obj['search_target']]['fp_list'][0]['output_fp']
                return_result[input_generator_name]['event_tags'][event_obj['event']] = convert_to_dct(search_target_fp, event_obj['fraction'])
        elif input_sample_index == 2:
            for event_obj in DctRunTimeGenerator.BROWSER_VISUAL_EVENT_POINTS['forward_search']:
                search_target_fp = crop_data_dict[event_obj['search_target']]['fp_list'][0]['output_fp']
                return_result[input_generator_name]['event_tags'][event_obj['event']] = convert_to_dct(search_target_fp, event_obj['fraction'])

        return return_result


    def generate_result(self, input_data, input_global_result):
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

        # compare images
        compare_setting = {'default_fps': input_data['default_fps'], 'event_points': self.BROWSER_VISUAL_EVENT_POINTS,
                           'generator_name': self.__class__.__name__, 'skip_status_bar_fraction': self.SKIP_STATUS_BAR_FRACTION,
                           'exec_timestamp_list': input_data['exec_timestamp_list']}
        compare_result = compare_with_sample_image_multi_process(input_data['sample_result'], input_image_list, compare_setting)

        return compare_result




