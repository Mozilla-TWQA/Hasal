import os
import cv2
import time
import shutil
from ..common.imageUtil import get_search_range
from ..common.logConfig import get_logger


logger = get_logger(__name__)


class Cv2Converter(object):

    def generate_result(self, input_data):
        search_range = []
        return_result = {}
        vidcap = cv2.VideoCapture(input_data['video_fp'])
        if hasattr(cv2, 'CAP_PROP_FPS'):
            header_fps = vidcap.get(cv2.CAP_PROP_FPS)
        else:
            header_fps = vidcap.get(cv2.cv.CV_CAP_PROP_FPS)
        if "current_fps" not in input_data:
            input_data['current_fps'] = header_fps
            logger.info('==== FPS from video header: ' + str(input_data['current_fps']) + '====')
        else:
            logger.info('==== FPS from log file: ' + str(input_data['current_fps']) + '====')
        real_time_shift = float(header_fps) / input_data['current_fps']
        if "exec_timestamp_list" in input_data:
            search_range = get_search_range(input_data['exec_timestamp_list'], input_data['current_fps'])

        if "output_image_name" in input_data:
            if os.path.exists(input_data['output_img_dp']) is False:
                os.mkdir(input_data['output_img_dp'])
            str_image_fp = os.path.join(input_data['output_img_dp'], input_data['output_image_name'])
            result, image = vidcap.read()
            cv2.imwrite(str_image_fp, image)
        else:
            io_times = 0
            img_cnt = 0
            if os.path.exists(input_data['output_img_dp']):
                shutil.rmtree(input_data['output_img_dp'])
            os.mkdir(input_data['output_img_dp'])
            start_time = time.time()
            while True:
                img_cnt += 1
                bol_write_flag = False
                in_search_flag = False
                str_image_fn = "image_%05d.bmp" % img_cnt
                str_image_fp = os.path.join(input_data['output_img_dp'], str_image_fn)
                if not input_data.get('exec_timestamp_list') or (search_range[0] <= img_cnt <= search_range[3]):
                    result, image = vidcap.read()
                    cv2.imwrite(str_image_fp, image)
                    bol_write_flag = True
                    in_search_flag = True
                    io_times += 1
                else:
                    result = vidcap.grab()
                return_result[str_image_fn] = {'fp': str_image_fp, 'time_seq': vidcap.get(0) * real_time_shift, 'write_to_file': bol_write_flag, 'in_search_flag': in_search_flag}
                if not result:
                    break
            end_time = time.time()
            elapsed_time = end_time - start_time
            logger.debug("Actual %s Images IO Time Elapsed: [%s]" % (str(io_times), elapsed_time))
        return return_result
