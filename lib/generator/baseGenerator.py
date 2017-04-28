import os
import json
import copy
import shutil
import tempfile
from ..common.commonUtil import CommonUtil
from ..common.commonUtil import CalculationUtil
from ..common.commonUtil import StatusRecorder


class BaseGenerator(object):

    def __init__(self, index_config, exec_config, online_config, global_config, input_env):
        self.index_config = index_config
        self.exec_config = exec_config
        self.online_config = online_config
        self.global_config = global_config
        self.status_recorder = StatusRecorder(global_config['default-running-statistics-fn'])
        self.env = input_env

    def record_runtime_current_status(self, input_runtime_value):
        if input_runtime_value == 0:
            self.status_recorder.record_current_status(
                {self.status_recorder.STATUS_IMG_COMPARE_RESULT: self.status_recorder.ERROR_EVENT_IMAGE_BOTH_SAME})
        elif input_runtime_value == -1:
            self.status_recorder.record_current_status(
                {self.status_recorder.STATUS_IMG_COMPARE_RESULT: self.status_recorder.ERROR_EVENT_IMAGE_LESS_THAN_2})
        else:
            self.status_recorder.record_current_status(
                {self.status_recorder.STATUS_IMG_COMPARE_RESULT: self.status_recorder.PASS_IMG_COMPARE_RESULT})

    def init_result_dict_variable(self, default_number_list, default_list_list):
        init_result_dict = {'description': self.env.test_method_doc}
        for init_number_key in default_number_list:
            init_result_dict[init_number_key] = 0
        for init_list_key in default_list_list:
            init_result_dict[init_list_key] = []
        return init_result_dict

    def generate_update_result_for_ft(self, input_update_result, input_compare_result, input_run_time_dict):
        update_result = copy.deepcopy(input_update_result)
        update_result['total_run_no'] += 1
        update_result['detail'].extend(input_compare_result['running_time_result'])
        if input_compare_result['run_time'] <= 0:
            update_result['error_no'] += 1
        else:
            update_result['time_list'].append(input_run_time_dict)
        update_result['video_fp'] = self.env.video_output_fp
        update_result['web_app_name'] = self.env.web_app_name
        update_result['revision'] = self.online_config['perfherder-revision']
        update_result['pkg_platform'] = self.online_config['perfherder-pkg-platform']
        return update_result

    def generate_update_result_for_runtime(self, input_update_result, input_compare_result, input_run_time_dict):
        update_result = copy.deepcopy(input_update_result)
        update_result['total_run_no'] += 1
        update_result['detail'].extend(input_compare_result['running_time_result'])
        if input_compare_result['run_time'] <= 0:
            update_result['error_no'] += 1
        else:
            update_result['total_time'] += input_compare_result['run_time']
            update_result['time_list'].append(input_run_time_dict)
        if len(update_result['time_list']) >= self.exec_config['max-run'] and self.index_config['drop-outlier-flag']:
            drop_outlier_list, _ = CalculationUtil.remove_outlier(update_result['time_list'], 'run_time')
            sorted_list, median_time_index, median, mean, sigma, min_value, max_value = CalculationUtil.get_median_avg_sigma_value(
                drop_outlier_list, 'run_time')
        else:
            sorted_list, median_time_index, median, mean, sigma, min_value, max_value = CalculationUtil.get_median_avg_sigma_value(
                update_result['time_list'], 'run_time')
        update_result['max_time'] = max_value
        update_result['min_time'] = min_value
        update_result['med_time'] = median
        update_result['avg_time'] = mean
        update_result['std_dev'] = sigma
        update_result['video_fp'] = self.env.video_output_fp
        update_result['web_app_name'] = self.env.web_app_name
        update_result['revision'] = self.online_config['perfherder-revision']
        update_result['pkg_platform'] = self.online_config['perfherder-pkg-platform']
        return sorted_list, median_time_index, update_result

    def output_runtime_result_video(self, running_time_result, suite_upload_dp):
        start_fp = None
        end_fp = None
        for event_data in running_time_result:
            if 'start' in event_data:
                start_fp = event_data['start']
            if 'end' in event_data:
                end_fp = event_data['end']
        if not start_fp or not end_fp:
            return None
        else:
            if os.path.exists(os.path.join(os.path.dirname(start_fp), self.global_config['default-search-target-browser'])):
                source_dp = os.path.join(os.path.dirname(start_fp), self.global_config['default-search-target-browser'])
            else:
                source_dp = os.path.dirname(start_fp)
            img_list = os.listdir(source_dp)
            img_list.sort(key=CommonUtil.natural_keys)
            start_fn = os.path.basename(start_fp)
            end_fn = os.path.basename(end_fp)
            file_ext = os.path.splitext(start_fn)[1]
            extended_range = self.index_config['video-recording-fps']
            start_index = max(0, img_list.index(start_fn) - extended_range)
            end_index = min(len(img_list) - 1, img_list.index(end_fn) + extended_range)
            tempdir = tempfile.mkdtemp()
            count = 0
            for img_index in range(start_index, end_index + 1):
                imf_fp = os.path.join(source_dp, img_list[img_index])
                new_img_fp = os.path.join(tempdir, '{0:05d}'.format(count) + file_ext)
                shutil.copyfile(imf_fp, new_img_fp)
                count += 1

        codec = "ffmpeg"
        source = " -i " + os.path.join(tempdir, "%05d" + file_ext)
        fps = " -r " + str(self.index_config['video-recording-fps'])
        video_format = " -pix_fmt yuv420p"
        video_out = " " + self.env.converted_video_output_fp
        command = codec + source + fps + video_format + video_out
        os.system(command)
        shutil.rmtree(tempdir)

        upload_case_name = "_".join(self.env.output_name.split("_")[2:-1])
        upload_case_dp = os.path.join(suite_upload_dp, upload_case_name)
        if os.path.exists(upload_case_dp) is False:
            os.mkdir(upload_case_dp)
        if os.path.exists(self.env.converted_video_output_fp):
            shutil.move(self.env.converted_video_output_fp, upload_case_dp)

    @staticmethod
    def output_ipynb_file(global_config, index_config, output_result_dir):

        # init result fp and ipynb template fp
        input_result_fp = global_config['default-result-fn']
        input_ipynb_template_fp = os.path.join(os.path.abspath(global_config['ipynb-template-default-dn']), index_config['ipynb-template-name'])
        result_data = CommonUtil.load_json_file(input_result_fp)
        converted_format_dict = {}

        # store result by case_name
        if result_data:
            for case_full_name in result_data:
                case_name = case_full_name.split("_", 2)[-1]
                if case_name in converted_format_dict:
                    converted_format_dict[case_name].update({case_full_name: result_data[case_full_name]})
                else:
                    converted_format_dict[case_name] = {case_full_name: result_data[case_full_name]}
            for c_name in converted_format_dict:
                case_result_fp = os.path.join(output_result_dir, c_name, c_name + ".json")
                output_ipynb_fp = os.path.join(output_result_dir, c_name, c_name + ".ipynb")
                with open(case_result_fp, 'w') as fh:
                    json.dump(converted_format_dict[c_name], fh)
                fig_number = len(converted_format_dict[c_name].keys())

                # output ipynb file
                CommonUtil.execute_runipy_cmd(input_ipynb_template_fp, output_ipynb_fp, input_data_fp=case_result_fp,
                                              input_fig_number=fig_number)

    @staticmethod
    def output_suite_result(global_config, index_config, exec_config, output_result_dir):
        # generate ipynb file
        if exec_config['output-result-ipynb-file']:
            BaseGenerator.output_ipynb_file(global_config, index_config, output_result_dir)

        # move statistics file to result folder
        running_statistics_fp = os.path.join(os.getcwd(), global_config['default-running-statistics-fn'])
        if os.path.exists(running_statistics_fp):
            shutil.move(running_statistics_fp, output_result_dir)

        # copy current result file to result folder
        result_fp = os.path.join(os.getcwd(), global_config['default-result-fn'])
        if os.path.exists(result_fp):
            shutil.copy(result_fp, output_result_dir)
