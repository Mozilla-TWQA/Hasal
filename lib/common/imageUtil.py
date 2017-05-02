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
from logConfig import get_logger

logger = get_logger(__name__)


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
    @param input_sample_dp: input sample folder path
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
    search_range = get_search_range(input_settings['exec_timestamp_list'], input_settings['default_fps'],
                                    len(input_image_data), search_margin)
    total_search_range = input_settings['default_fps'] * search_margin * 2
    if input_settings['search_direction'] == 'backward_search':
        start_index = search_range[1] - 1
        end_index = max(search_range[0], start_index - total_search_range)
    elif input_settings['search_direction'] == 'forward_search':
        start_index = search_range[2] - 1
        end_index = min(search_range[3] - 1, start_index + total_search_range)
    else:
        start_index = 0
        end_index = 0
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

    for event_point in input_settings['event_points'][input_settings['search_direction']]:
        event_name = event_point['event']
        search_target = event_point['search_target']

        logger.info('Comapre event [{event_name}] at [{search_target}]: {forward_backward} from {start} to {end}'
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
            if event_name == 'first_paint':
                skip_status_bar_fraction = input_settings['skip_status_bar_fraction']
            else:
                skip_status_bar_fraction = 1.0

            while search_count < total_search_range:
                if forward_search and img_index > end_index:
                    break
                elif not forward_search and img_index < end_index:
                    break
                search_count += 1

                # transfer image index to image fn key
                img_fn_key = image_fn_list[img_index]
                if search_target in input_image_data[img_fn_key]:
                    current_img_dct = convert_to_dct(input_image_data[img_fn_key][search_target], skip_status_bar_fraction)
                    # assign customized threshold to comparison function if its in settings list
                    threshold_value = input_settings.get('threshold', 0.0003)
                    compare_result, diff_rate = compare_two_images(sample_dct, current_img_dct, threshold_value)

                    # record the diff_rate
                    diff_rate_list.append((event_name, img_fn_key, diff_rate))

                    if compare_result:
                        logger.debug('Match {img_index} {img_filename}'.format(img_index=img_index,
                                                                               img_filename=img_fn_key))

                        if img_index == start_index:
                            logger.debug(
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
                            img_index = start_index
                        else:
                            # shift one index to avoid boundary matching two events at the same time
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
                            result_list.append({event_name: input_image_data[img_fn_key]['fp'], 'time_seq': input_image_data[img_fn_key]['time_seq']})
                            logger.debug("Comparing %s point end %s" % (event_name, time.strftime("%c")))
                            break
                    else:
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
    match = False
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
