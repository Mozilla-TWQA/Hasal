import os
import cv2
import time
import copy
import heapq
import numpy as np
import pprint
import threading
from PIL import Image
from multiprocessing import Process, Manager
from commonUtil import CommonUtil
from commonUtil import StatusRecorder
from logConfig import get_logger

logger = get_logger(__name__)


class CropRegion(object):
    """
    Here's the Crop Region Fig

    |----------------------------------|  ---             ---
    |        |                         |   ^               ^
    | Tab  X |                         |   V <= TAB_VIEW   |
    |----------------------------------|  ---              |
    |                                  |   ^               |
    |                                  |   |               |
    |                                  |   |               |
    |            Web Page              |   | <= VIEWPORT   | <= BROWSER
    |                                  |   |               |
    |                                  |   |               |
    |                                  |   v               v
    |----------------------------------|  ---             ---

    |----------------------------------|  ---
    | $ Terminal> _                    |   ^ <= TERMINAL
    |                                  |   V
    |----------------------------------|  ---
    """
    # Hasal do NOT crop the original
    ORIGINAL = 'original'

    VIEWPORT = 'viewport'
    TAB_VIEW = 'tab_view'
    BROWSER = 'browser'
    TERMINAL = 'terminal'

    # Fraction settings for simple height cut
    FULL_REGION_FRACTION = 1.0
    SKIP_STATUS_BAR_FRACTION = 0.95

    @staticmethod
    def generate_customized_visual_event_points(sikuli_status, visual_event_points):
        """
        Looping the visual_event_points object, for example:
            {
                'fordward_search': [{'event': 'end', 'search_target': CropRegion.VIEWPORT, 'fraction': CropRegion.SKIP_STATUS_BAR_FRACTION, 'shift_result': True},
                                    {'event': 'foobar', 'search_target': CropRegion.TERMINAL, 'fraction': CropRegion.FULL_REGION_FRACTION, 'shift_result': True}],
                'backward_search': [{'event': 'xyztest', 'search_target': CropRegion.VIEWPORT, 'fraction': CropRegion.SKIP_STATUS_BAR_FRACTION, 'shift_result': True},
                                    {'event': 'start', 'search_target': CropRegion.TERMINAL, 'fraction': CropRegion.FULL_REGION_FRACTION, 'shift_result': True}]
            }

        And then checking with region_override from Sikuli status:
            {
                'end':                                  # reference event name key
                {
                    'event': 'end',                     # event name
                    'direction': 'backward',            # no use now
                    'search_target': 'end_region',      # customized region name
                    'shift_result': true,               # shift one image base on direction
                    'fraction': 1,                      # Full Fraction
                    'x': 94,                            # x
                    'y': 87,                            # y
                    'w': 94,                            # width
                    'h': 99                             # height
                }
            }
        @param sikuli_status: the sikuli status dict object, which comes from stat JSON file.
        @param visual_event_points: the visual_event_point dict object, which comes from Generator instance.
        @return: new visual_event_points dict object.
        """
        region_override_dict = sikuli_status[StatusRecorder.SIKULI_KEY_REGION_OVERRIDE]

        for direction, origin_event_list in visual_event_points.items():
            is_override = False
            new_event_list = []
            for origin_event_obj in origin_event_list:
                is_match = False
                for sikuli_event_key, sikuli_event_obj in region_override_dict.items():
                    if sikuli_event_obj.get('event', '') == origin_event_obj.get('event', ''):
                        is_override = True
                        is_match = True
                        new_event_obj = copy.deepcopy(origin_event_obj)
                        new_event_obj['search_target'] = sikuli_event_obj.get('search_target')
                        new_event_obj['shift_result'] = sikuli_event_obj.get('shift_result')
                        # We should compare full customized region
                        new_event_obj['fraction'] = CropRegion.FULL_REGION_FRACTION
                        new_event_obj['x'] = sikuli_event_obj.get('x')
                        new_event_obj['y'] = sikuli_event_obj.get('y')
                        new_event_obj['w'] = sikuli_event_obj.get('w')
                        new_event_obj['h'] = sikuli_event_obj.get('h')
                        break
                if is_match:
                    new_event_list.append(new_event_obj)
                else:
                    new_event_list.append(origin_event_obj)

            if is_override:
                visual_event_points[direction] = new_event_list
                logger.debug('Replace Visual Event Point [{dir}] from\n {origin_evt_list}\nto\n {new_evt_list}'
                             .format(dir=direction,
                                     origin_evt_list=origin_event_list,
                                     new_evt_list=new_event_list))
        return visual_event_points


def crop_image(input_sample_fp, output_sample_fp, coord=[]):
    """
    For template region matching.
    @param input_sample_fp: target sample fp for cropping data
    @param output_sample_fp: output sample fp
    @param coord: region area
    @return: output_sample_fp
    """
    img = cv2.imread(input_sample_fp)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    w, h = img_gray.shape[::-1]
    if (not coord or len(coord) != 2 or type(coord[0]) is not tuple or len(coord[0]) != 2 or type(
            coord[1]) is not tuple or len(coord[1]) != 2):
        coord = [(0, 0), (w, h)]
        logger.warning("Incorrect coordinates, using fully image crop")
    else:
        for i in range(2):
            for j in range(2):
                new_val = coord[i][j]
                if coord[i][j] < 0:
                    new_val = 0
                elif j == 0 and coord[i][j] > w:
                    new_val = w
                elif j == 1 and coord[i][j] > h:
                    new_val = h
                if new_val != coord[i][j]:
                    new_xy = [coord[i][0], coord[i][1]]
                    list_index = int(j == 0)
                    new_xy[list_index] = coord[i][list_index]
                    new_xy[j] = new_val
                    coord[i] = tuple(new_xy)
                    logger.warning("Incorrect coordinates, set %s %s coordinate to %s" % (
                        ["origin", "target"][i], str(unichr(120 + j)), str(new_val)))
    logger.info("Crop image range: " + str(coord))
    if coord[0][0] < coord[1][0] and coord[0][1] < coord[1][1]:
        crop_img = img[coord[0][1]:coord[1][1], coord[0][0]:coord[1][0]]
    elif coord[0][0] > coord[1][0] and coord[0][1] > coord[1][1]:
        crop_img = img[coord[1][1]:coord[0][1], coord[1][0]:coord[0][0]]
    elif coord[0][0] < coord[1][0] and coord[0][1] > coord[1][1]:
        crop_img = img[coord[1][1]:coord[0][1], coord[0][0]:coord[1][0]]
    else:
        crop_img = img[coord[0][1]:coord[1][1], coord[1][0]:coord[0][0]]
    cv2.imwrite(output_sample_fp, crop_img)
    return output_sample_fp


def convert_to_dct(image_fp, skip_status_bar_fraction=1.0):
    """

    @param image_fp:
    @param skip_status_bar_fraction:
    @return:
    """
    dct_obj = None
    try:
        img_obj = cv2.imread(image_fp)
        height, width, channel = img_obj.shape
        height = int(height * skip_status_bar_fraction) - int(height * skip_status_bar_fraction) % 2
        img_obj = img_obj[:height][:][:]
        img_gray = np.zeros((height, width))
        for each_channel in range(channel):
            img_gray += img_obj[:, :, each_channel]
        img_gray /= channel
        img_dct = img_gray / 255.0
        dct_obj = cv2.dct(img_dct)
    except Exception as e:
        logger.error(e)
    return dct_obj


def find_browser_view(viewport, tab_view):
    browser_view = {'x': viewport['x'], 'y': tab_view['y'], 'width': viewport['width'],
                    'height': viewport['y'] + viewport['height'] - tab_view['y']}
    return browser_view


def generate_crop_data(input_target_list, crop_target_list):
    """
    generate crop data for crop images functions
    @param input_target_list: target obj list, for example {'fp': 'xxxx, 'write_to_file': True}
    @param crop_target_list: crop target area list, for example {'viewport': {'x': 2, 'y', ..}}
    @return: integrate crop data, for example: {'fp_list': [ {'input_fp':xxx, 'output_fp':xxx}], 'crop_area': {'x':2, 'y':3, ..}}
    """
    crop_data_dict = {}
    for input_target in input_target_list:
        if 'write_to_file' in input_target and input_target['write_to_file']:
                for crop_taget_name in crop_target_list:
                    input_fn_name = os.path.basename(input_target['fp'])
                    input_parent_dp = os.path.dirname(input_target['fp'])
                    output_dp = os.path.join(input_parent_dp, crop_taget_name)
                    if not os.path.exists(output_dp):
                        os.mkdir(output_dp)
                    output_fp = os.path.join(output_dp, input_fn_name)
                    if crop_taget_name in crop_data_dict:
                        crop_data_dict[crop_taget_name]['fp_list'].append(
                            {'input_fp': input_target['fp'], 'output_fp': output_fp})
                    else:
                        crop_data_dict[crop_taget_name] = {
                            'fp_list': [{'input_fp': input_target['fp'], 'output_fp': output_fp}],
                            'crop_area': crop_target_list[crop_taget_name]}

    return crop_data_dict


def crop_images(input_crop_images_data):
    """
    multi-processing to crop different regions from original images
    @param input_crop_images_data:
    @return:
    """
    p_list = []
    for region_key in input_crop_images_data:
        args = [input_crop_images_data[region_key]]
        p_list.append(Process(target=multithread_crop_images, args=args))
        p_list[-1].start()
    for p in p_list:
        p.join()


def generate_chunks(input_list, input_chunk_no):
    """

    @param input_list:
    @param input_chunk_no:
    @return:
    """

    return_list = []
    average_index = len(input_list) / float(input_chunk_no)
    last_index = 0.0
    while last_index < len(input_list):
        return_list.append(input_list[int(last_index):int(last_index + average_index)])
        last_index += average_index
    return return_list


def multithread_crop_images(input_image_data, default_thread_no=5):
    """
    @param input_image_data:
    @param default_thread_no:
    @return:
    """
    chunk_list = generate_chunks(input_image_data['fp_list'], default_thread_no)
    p_list = []
    for index in range(len(chunk_list)):
        args = [chunk_list[index], input_image_data['crop_area']]
        p_list.append(threading.Thread(target=crop_multiple_images, args=args))
        p_list[-1].start()
    for p in p_list:
        p.join()


def crop_multiple_images(input_image_list, input_crop_area):
    """

    @param input_image_list:
    @param input_crop_area:
    @return:
    """
    if input_crop_area['width'] % 2:
        input_crop_area['width'] -= 1
    if input_crop_area['height'] % 2:
        input_crop_area['height'] -= 1
    crop_region = [input_crop_area['x'], input_crop_area['y'],
                   input_crop_area['x'] + input_crop_area['width'],
                   input_crop_area['y'] + input_crop_area['height']]
    for input_image_data in input_image_list:
        try:
            if os.path.exists(input_image_data['output_fp']):
                # logger.debug("crop file[%s] already exists, skip crop actions!" % input_image_data['output_fp'])
                continue
            else:
                if os.path.isfile(input_image_data['input_fp']):
                    # logger.debug("Crop file [%s] with crop area [%s]" % (input_image_data['input_fp'], crop_region))
                    src_img = Image.open(input_image_data['input_fp'])
                    dst_img = src_img.crop(crop_region)
                    dst_img.save(input_image_data['output_fp'])
                else:
                    logger.warning("Incorrect image format of file during crop images: [%s]" % input_image_data['input_fp'])
                    continue
        except Exception as e:
            logger.error(e)


def compare_with_sample_image_multi_process(input_sample_data, input_image_data, input_settings):
    """
    Compare sample images, return matching list.
    return example:
        [
            {'event': 'start', 'file': 'foo/bar/9487.bmp', 'time_seq': 5487.9487},
            {'event': 'end', 'file': 'foo/bar/9527.bmp', 'time_seq': 5566.5566}, ...
        ]
    @param input_sample_data:
    @param input_image_data:
    @param input_settings: the comparing settings.
            ex:
            {
                'default_fps',
                'event_points',
                'generator_name',
                'skip_status_bar_fraction',
                'exec_timestamp_list',
                'threshold',
                'search_margin'
            }
    @return: the matching result list
    """
    manager = Manager()
    result_list = manager.list()
    diff_rate_list = manager.list()
    p_list = []
    for search_direction in input_settings['event_points'].keys():
        parallel_run_settings = copy.deepcopy(input_settings)
        parallel_run_settings['search_direction'] = search_direction
        args = [input_sample_data, input_image_data, parallel_run_settings, result_list, diff_rate_list]
        p_list.append(Process(target=parallel_compare_image, args=args))
        p_list[-1].start()
    for p in p_list:
        p.join()
    map_result_list = sorted(map(dict, result_list), key=lambda k: k['time_seq'])

    logger.info('The threshold in comparing settings: {}'.format(input_settings.get('threshold', None)))
    logger.info(map_result_list)
    if len(map_result_list) == 0:
        logger.info('Images miss with sample.')
    else:
        logger.info('Images HIT with sample!')

    # the data in diff_rate_list will be (event_name, img_fn_key, diff_rate)
    diff_rate_by_event = {}
    for event_name, img_fn_key, diff_val in diff_rate_list:
        if event_name not in diff_rate_by_event:
            diff_rate_by_event[event_name] = list()
        # append (img_fn_key, diff_rate) into event's diff_rate list
        diff_rate_by_event[event_name].append((img_fn_key, diff_val))

    for event, img_and_diff in diff_rate_by_event.items():
        # data format (img_fn_key, diff_rate), find 3 smallest by diff_rate
        top_3_smallest_diff_list = heapq.nsmallest(3, img_and_diff, key=lambda val_tuple: val_tuple[1])
        logger.info('Top 3 Smallest Difference of Event [{event}]:\n{min_diff_rate}'.
                    format(event=event, min_diff_rate=pprint.pformat(top_3_smallest_diff_list)))

    return map_result_list


def get_search_range(input_time_stamp, input_fps, input_image_list_len=0, input_cover_sec=10):
    ref_start_point = input_time_stamp[1] - input_time_stamp[0]
    ref_end_point = input_time_stamp[2] - input_time_stamp[0]
    if input_image_list_len:
        search_range = [
            # For finding the beginning, the range cannot start less than zero.
            max(int((ref_start_point - input_cover_sec) * input_fps), 0),
            min(int((ref_start_point + input_cover_sec) * input_fps), input_image_list_len - 1),
            # For finding the end, the range cannot start less than zero.
            max(int((ref_end_point - input_cover_sec) * input_fps), 0),
            min(int((ref_end_point + input_cover_sec) * input_fps), input_image_list_len - 1)]
    else:
        search_range = [
            # For finding the beginning, the range cannot start less than zero.
            max(int((ref_start_point - input_cover_sec) * input_fps), 0),
            int((ref_start_point + input_cover_sec) * input_fps),
            # For finding the end, the range cannot start less than zero.
            max(int((ref_end_point - input_cover_sec) * input_fps), 0),
            int((ref_end_point + input_cover_sec) * input_fps)]
    logger.info("Image Comparison search range [%s] when image list len is [%s]: " % (str(search_range), str(input_image_list_len)))
    return search_range


def parallel_compare_image(input_sample_data, input_image_data, input_settings, result_list, diff_rate_list):
    # init value
    sample_dct = None
    image_fn_list = copy.deepcopy(input_image_data.keys())
    image_fn_list.sort(key=CommonUtil.natural_keys)

    # generate search range
    search_margin = input_settings.get('search_margin', 10)
    search_range = get_search_range(input_settings['exec_timestamp_list'],
                                    input_settings['default_fps'],
                                    len(input_image_data),
                                    search_margin)
    total_search_range = input_settings['default_fps'] * search_margin * 2
    search_direction = input_settings.get('search_direction', None)
    if search_direction == 'backward_search':
        start_index = search_range[1] - 1
        end_index = max(search_range[0], start_index - total_search_range)
    elif search_direction == 'forward_search':
        start_index = search_range[2] - 1
        end_index = min(search_range[3] - 1, start_index + total_search_range)
    else:
        start_index = 0
        end_index = 0

    # raise exception when no search direction, or image data length is less then range
    if not search_direction or (start_index == 0 and end_index == 0):
        raise Exception('There is no search_direction. settings: {}'.format(input_settings))
    if search_range[0] > len(input_image_data) or search_range[2] > len(input_image_data):
        raise Exception('The image length is less then start of search range. '
                        'Image Length: {img_len}, search range: {range}'
                        .format(img_len=len(input_image_data), range=search_range))

    search_count = 0
    img_index = start_index
    if end_index > start_index:
        forward_search = True
    else:
        forward_search = False
    logger.info('Starting {forward_backward} Comparing, from {start} to {end} ...'
                .format(forward_backward='Forward' if forward_search else 'Backward',
                        start=start_index,
                        end=end_index))

    for event_point in input_settings['event_points'][search_direction]:
        event_name = event_point['event']
        search_target = event_point['search_target']
        fraction = event_point['fraction']

        logger.info('Compare event [{event_name}] at [{search_target}]: {forward_backward} from {start} to {end}'
                    .format(event_name=event_name,
                            search_target=search_target,
                            forward_backward='Forward' if forward_search else 'Backward',
                            start=start_index,
                            end=end_index))

        shift_result_flag = event_point.get('shift_result', False)
        # get corresponding dct by event name
        for sample_index in input_sample_data:
            sample_data = input_sample_data[sample_index]
            if event_name in sample_data[input_settings['generator_name']]['event_tags']:
                sample_dct = sample_data[input_settings['generator_name']]['event_tags'][event_name]
                break

        if sample_dct is None:
            logger.error("Can't find the specify event[%s] in your sample data[%s]!" % (event_name, input_sample_data))
        else:
            while search_count < total_search_range:
                if forward_search and img_index > end_index:
                    break
                elif not forward_search and img_index < end_index:
                    break
                search_count += 1

                # transfer image index to image fn key
                img_fn_key = image_fn_list[img_index]
                if search_target in input_image_data[img_fn_key]:

                    compare_result = False
                    current_img_fp = input_image_data[img_fn_key][search_target]
                    current_img_dct = convert_to_dct(current_img_fp, fraction)

                    if current_img_dct is None:
                        logger.error('Cannot convert the image [{image_file}] to DCT object for specify event[{event}]!'
                                     .format(event=event_name, image_file=current_img_fp))
                    else:
                        # assign customized threshold to comparison function if its in settings list
                        threshold_value = input_settings.get('threshold', 0.0003)
                        compare_result, diff_rate = compare_two_images(sample_dct, current_img_dct, threshold_value)

                        # record the diff_rate
                        diff_rate_list.append((event_name, img_fn_key, diff_rate))

                    if compare_result:
                        # when match (compare_result is True), check the current image index
                        logger.debug('Match {img_index} {img_filename}'.format(img_index=img_index,
                                                                               img_filename=img_fn_key))
                        if img_index == start_index:
                            # when current index is the same as start index, it should expend the search range.
                            logger.info(
                                "Find matched file in boundary of search range, event point might out of search range.")
                            if forward_search:
                                # if start index is already at boundary then break
                                if start_index == search_range[0]:
                                    break
                                start_index = max(img_index - total_search_range / 2, search_range[0])
                                logger.debug('Change start: {start}'.format(start=start_index))
                            else:
                                # if start index is already at boundary then break
                                if start_index == search_range[3] - 1:
                                    break
                                start_index = min(img_index + total_search_range / 2, search_range[3] - 1)
                                logger.debug('Change start: {start}'.format(start=start_index))
                            # compare the same image, reset current image index from new start
                            img_index = start_index
                        else:
                            # when current index is not start index, it really match!
                            # shift index to avoid boundary if we want to match more than one events at the same time.
                            if forward_search:
                                start_index = img_index - 1
                                end_index = min(search_range[3] - 1, start_index + total_search_range)
                                logger.debug('Change start: {start}; end: {end}'.format(start=start_index,
                                                                                        end=end_index))
                            else:
                                start_index = img_index + 1
                                end_index = max(search_range[0], start_index - total_search_range)
                                logger.debug('Change start: {start}; end: {end}'.format(start=start_index,
                                                                                        end=end_index))

                            # using shifted image index as result if search result's flag is set
                            if shift_result_flag:
                                img_fn_key = image_fn_list[start_index]
                            search_count = 0
                            result_list.append({'event': event_name, 'file': input_image_data[img_fn_key]['fp'], 'time_seq': input_image_data[img_fn_key]['time_seq']})
                            logger.debug("Comparing %s point end %s" % (event_name, time.strftime("%c")))
                            # compare next image, reset current image index from start
                            img_index = start_index
                            break
                    else:
                        # when not match (compare_result is False), compare next image
                        if forward_search:
                            img_index += 1
                        else:
                            img_index -= 1
                else:
                    if forward_search:
                        img_index += 1
                    else:
                        img_index -= 1


def compare_two_images(dct_obj_1, dct_obj_2, threshold):
    """
    Comparing two input DCT objects, if the difference rate less than threshold, then return True, otherwise False.
    @param dct_obj_1: input DCT object
    @param dct_obj_2: input DCT object
    @param threshold: the comparing threshold
    @return: (True/Fasle of match, the different rate of two input DCT objects)
    """
    match = False
    # setup default diff rate
    diff_rate = 2
    try:
        row1, cols1 = dct_obj_1.shape
        row2, cols2 = dct_obj_2.shape

        if (row1 == row2) and (cols1 == cols2):
            diff_rate = np.sum(np.absolute(np.subtract(dct_obj_1, dct_obj_2))) / (row1 * cols1)
            if diff_rate <= threshold:
                match = True
    except Exception as e:
        logger.error(e)
    return match, diff_rate
