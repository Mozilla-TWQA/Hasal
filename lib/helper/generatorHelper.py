import time
import json
import importlib
from lib.common.commonUtil import CommonUtil
from lib.common.commonUtil import StatusRecorder
from lib.common.logConfig import get_logger

logger = get_logger(__name__)
RET_SUCCESSS = 0


def validate_data(validator_settings, validator_data):
    """

    @param validator_settings: use validator name as key to define validator module and module path in dict type
    @param validator_data: use validator name as key to define validator data in dict type
    @return: validate_result , and validator name as key, include with validate result and output_result
    """
    validator_result = {'validate_result': False}
    for validator_name in validator_settings['modules'].keys():
        validator_class = getattr(importlib.import_module(validator_settings['modules'][validator_name]['path']),
                                  validator_name)
        validator_obj = validator_class()
        validate_result = validator_obj.validate(validator_data[validator_name])
        if not validate_result:
            logger.warning(
                "Validator[%s] validate data failed, output is [%s]." % (validator_name, validator_obj.get_output()))
            return validator_result
        else:
            validator_result[validator_name] = {'validate_result': validate_result,
                                                'output_result': validator_obj.get_output()}
    validator_result['validate_result'] = True

    # dump validate result to status file
    objStatusRecorder = StatusRecorder(validator_settings['status_file'])
    objStatusRecorder.record_current_status({objStatusRecorder.STATUS_VALIDATOR_RESULT: validator_result})
    return validator_result


def run_modules(module_settings, module_data):
    """

    @param module_settings:
    @param module_data:
    @return:
    """
    module_result = {}
    for module_name in module_settings['modules'].keys():
        module_class = getattr(importlib.import_module(module_settings['modules'][module_name]['path']), module_name)
        module_obj = module_class()
        start_time = time.time()
        module_result[module_name] = module_obj.generate_result(module_data)
        last_end = time.time()
        elapsed_time = last_end - start_time
        logger.debug("Module [%s] Time Elapsed: [%s]" % (module_name, elapsed_time))
    return module_result


def get_json_data(input_fp, initial_timestamp_name):
    # TODO: need to support multiple sample timestamps in the future
    try:
        with open(input_fp, "r") as fh:
            timestamp = json.load(fh)
            logger.debug('Load timestamps: %s' % timestamp)
        timestamp_list = map(float, [timestamp[initial_timestamp_name], timestamp["t1"], timestamp["t2"]])
    except Exception as e:
        logger.error(e)
        logger.error('Make timestamp list be empty.')
        timestamp_list = []
    return timestamp_list


def calculate(env, global_config, exec_config, index_config, firefox_config, online_config, suite_upload_dp="", crop_data=None):
    """

    @param env: from lib.common.environment.py
    @param crop_data: sample crop data area
    @param calc_si: '1' or '0'
    @param waveform: 0~3
    @param revision:  upload to perfherder revision
    @param pkg_platform:  upload to perfherder pkg platform name
    @param suite_upload_dp: folder consolidate all execution result
    @param viewport: browser viewport region
    @return:
    """

    # validation data assign
    validator_data = {global_config['default-file-exist-validator-name']: {'check_fp_list': [env.video_output_fp]}}
    validator_settings = {'modules': {global_config['default-file-exist-validator-name']: {'path': global_config['default-file-exist-validator-module-path']}}}

    if CommonUtil.is_validate_fps(firefox_config):
        validator_data[global_config['default-fps-validator-name']] = {'recording_log_fp': env.recording_log_fp,
                                                                       'default_fps': index_config['video-recording-fps']}
        validator_settings['modules'][global_config['default-fps-validator-name']] = {'path': global_config['default-fps-validator-module-path']}
    validator_settings['status_file'] = global_config['default-running-statistics-fn']

    # will do the analyze after validate pass
    validate_result = validate_data(validator_settings, validator_data)

    exec_timestamp_list = get_json_data(env.DEFAULT_TIMESTAMP, env.INITIAL_TIMESTAMP_NAME)
    if validate_result['validate_result']:
        if not validate_result.get(global_config['default-fps-validator-name']):
            current_fps_value = index_config['video-recording-fps']
        else:
            current_fps_value = validate_result[global_config['default-fps-validator-name']]['output_result']
        # using different converter will introduce different time seq,
        # the difference range will between 0.000000000002 to 0.000000000004 ms (cv2 is lower than ffmpeg)
        converter_settings = {'modules': {index_config['image-converter-name']: {'path': index_config['image-converter-path']}}}
        converter_data = {
            index_config['image-converter-name']: {'video_fp': env.video_output_fp, 'output_img_dp': env.img_output_dp,
                                                   'convert_fmt': index_config['image-converter-format'],
                                                   'current_fps': current_fps_value,
                                                   'exec_timestamp_list': exec_timestamp_list}}
        converter_result = run_modules(converter_settings, converter_data[index_config['image-converter-name']])

        generator_name = index_config['module-name']
        generator_module_path = index_config['module-path']

        sample_settings = {'modules': {index_config['sample-converter-name']: {'path': index_config['sample-converter-path']}}}
        sample_data = {'sample_dp': env.img_sample_dp,
                       'configuration': {'generator': {generator_name: {'path': generator_module_path}}}}

        # {1:{'fp': 'xxcxxxx', 'RunTimeDctGenerator': 'dctobj', 'SpeedIndexGenerator': None, },
        #  2:{'fp':'xxxxx', 'SpeedIndexGenerator': None, 'crop_fp': 'xxxxxxx', 'viewport':'xxxxx'},
        #  }
        sample_result = run_modules(sample_settings, sample_data)
        generator_data = {'converter_result': converter_result[index_config['image-converter-name']], 'sample_result': sample_result[index_config['sample-converter-name']],
                          'exec_timestamp_list': exec_timestamp_list}

        generator_class = getattr(importlib.import_module(generator_module_path), generator_name)
        generator_obj = generator_class(index_config, exec_config, online_config, global_config, env)
        start_time = time.time()
        generator_result = generator_obj.generate_result(generator_data)
        last_end = time.time()
        elapsed_time = last_end - start_time
        logger.debug(generator_result)
        logger.debug("Generator [%s] Time Elapsed: [%s]" % (generator_name, elapsed_time))

        # record fps_stat
        objStatusRecorder = StatusRecorder(global_config['default-running-statistics-fn'])
        if validate_result.get(global_config['default-fps-validator-name'], {}).get('validate_result', True):
            objStatusRecorder.record_current_status({objStatusRecorder.STATUS_FPS_VALIDATION: 0})
        else:
            objStatusRecorder.record_current_status({objStatusRecorder.STATUS_FPS_VALIDATION: 1})

        # generate case result to json
        generator_obj.output_case_result(suite_upload_dp)
