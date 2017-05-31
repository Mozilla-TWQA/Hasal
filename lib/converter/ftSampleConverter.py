import os
import importlib
from ..common.imageUtil import crop_image
from ..common.logConfig import get_logger
from ..common.visualmetricsWrapper import find_image_viewport


logger = get_logger(__name__)


class FTSampleConverter(object):
    DEFAULT_SUPPORT_SAMPLE_FORMAT = ['.png']

    def generate_result(self, input_data):
        """

        @param input_data:
        @return:
        """
        return_result = {}

        # find viewport based on original captured sample
        orig_sample_fn = input_data.get('orig_sample', None)
        if not orig_sample_fn:
            viewport = None
        else:
            orig_sample_fp = os.path.join(input_data['sample_dp'], orig_sample_fn)
            viewport = find_image_viewport(orig_sample_fp)

        input_fn_list = os.listdir(input_data['sample_dp'])
        input_fn_list.sort()
        for sample_fn in input_fn_list:
            sample_fp = os.path.join(input_data['sample_dp'], sample_fn)
            sampe_root_name, sample_ext_name = os.path.splitext(sample_fp)
            if sample_ext_name in self.DEFAULT_SUPPORT_SAMPLE_FORMAT:
                sample_index = int(sampe_root_name.split("_")[-1])
                if not viewport:
                    return_result[sample_index] = {'fp': sample_fp, 'write_to_file': True}
                else:
                    return_result[sample_index] = {'fp': sample_fp, 'write_to_file': True, 'viewport': viewport}

                # based on assigned generator name create index value for each sample
                for generator_name in input_data['configuration']['generator']:
                    generator_class = getattr(importlib.import_module(input_data['configuration']['generator'][generator_name]['path']), generator_name)
                    generator_obj = generator_class(input_data['index_config'],
                                                    input_data['exec_config'],
                                                    input_data['online_config'],
                                                    input_data['global_config'],
                                                    input_data['input_env'])
                    return_result[sample_index].update(generator_obj.generate_sample_result(generator_name, return_result, sample_index))

                # base crop_data attribute will crop region for sample file, the output will be: rootname_crop.ext
                if 'crop_data' in input_data['configuration']:
                    if sample_index in input_data['configuration']['crop_data']:
                        sample_root_name, sample_ext_name = os.path.splitext(sample_fp)
                        crop_sample_fp = sample_root_name + "_crop" + sample_ext_name
                        return_result[sample_index]['crop_fp'] = crop_image(sample_fp, crop_sample_fp,
                                                                            input_data['configuration']['crop_data'][
                                                                                sample_index]['range'])
            else:
                logger.warning("Sample dp [%s] contain not supported extension files [%s]" % (input_data['sample_dp'], sample_fp))

        return return_result
