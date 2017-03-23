from dctRunTimeGenerator import DctRunTimeGenerator
from ..common.visualmetricsWrapper import calculate_progress_for_si
from ..common.visualmetricsWrapper import calculate_speed_index
from ..common.visualmetricsWrapper import calculate_perceptual_speed_index
from ..common.logConfig import get_logger

logger = get_logger(__name__)


class SpeedIndexGenerator(object):

    DEFAULT_DCTRUNTIME_GENERATOR_NAME = DctRunTimeGenerator.__class__.__name__

    @staticmethod
    def generate_sample_result(input_generator_name, input_sample_dict, input_sample_index):
        return DctRunTimeGenerator.generate_sample_result(input_generator_name, input_sample_dict, input_sample_index)

    def generate_result(self, input_data, input_global_result):
        """

        :param input_data:
        :param input_global_result:
        :return:
        """

        compare_result = {}

        if SpeedIndexGenerator.DEFAULT_DCTRUNTIME_GENERATOR_NAME in input_global_result:
            compare_result = input_global_result[SpeedIndexGenerator.DEFAULT_DCTRUNTIME_GENERATOR_NAME]
            si_progress = calculate_progress_for_si(compare_result['running_time_result'], input_global_result['merged_crop_image_list'])
            compare_result['speed_index'] = calculate_speed_index(si_progress)
        else:
            objdctruntimegenerator = DctRunTimeGenerator()
            compare_result = objdctruntimegenerator.generate_result(input_data, input_global_result)
            si_progress = calculate_progress_for_si(compare_result['running_time_result'], compare_result['merged_crop_image_list'])
            compare_result['speed_index'] = calculate_speed_index(si_progress)
            compare_result['perceptual_speed_index'] = calculate_perceptual_speed_index(si_progress)

        return compare_result
