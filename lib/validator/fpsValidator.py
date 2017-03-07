import os
import re
from collections import Counter
from baseValidator import BaseValidator
from ..common.logConfig import get_logger

logger = get_logger(__name__)


class FPSValidator(BaseValidator):

    def validate(self, input_validate_data):
        status_success = True
        status_fail = False
        fps_stat = status_success
        fps_return = 0
        tolerance = 0.03  # recording fps tolerance is set to 3%
        fps_frequency_threshold = 0.9  # fps frequency should be more than 90%
        if os.path.exists(input_validate_data['recording_log_fp']):
            with open(input_validate_data['recording_log_fp'], 'r') as fh:
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
                tolerance_fps_element = [item for item in all_fps_tuple if
                                         self.is_number_in_tolerance(item[0], input_validate_data['default_fps'], tolerance)]
                tolerance_fps_total_record = sum([item[1] for item in tolerance_fps_element])
                if float(tolerance_fps_total_record) / total_record >= fps_frequency_threshold:
                    fps_return = sum([item[0] * item[1] for item in tolerance_fps_element]) / tolerance_fps_total_record
                else:
                    fps_return = sum([item[0] * item[1] for item in all_fps_tuple]) / total_record
                    fps_stat = status_fail
        else:
            logger.warning("Recording log doesn't exist.")
            fps_stat = status_fail
        self.output = int(round(fps_return))
        return fps_stat

    def is_number_in_tolerance(self, number, default_fps, tolerance):
        return int(default_fps * (1 - tolerance)) <= number <= round(default_fps * (1 + tolerance))
