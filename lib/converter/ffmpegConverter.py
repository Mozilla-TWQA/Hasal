import os
import shutil
import subprocess


class FfmpegConverter(object):

    def generate_result(self, input_data):
        """

        @param input_data: should consist keys (output_img_dp, convert_fmt, video_fp, current_fps)
        @return: example result: {'img00001.bmp': {'fp': '/home/hasal/Hasal/output/images/img00001.bmp', 'time_seq': 12332434}}
        """
        return_result = {}
        if os.path.exists(input_data['output_img_dp']):
            shutil.rmtree(input_data['output_img_dp'])
        os.mkdir(input_data['output_img_dp'])
        output_img_fmt = input_data['output_img_dp'] + os.sep + 'image_%05d.' + input_data['convert_fmt'].lower()
        cmd_list = ['ffmpeg', '-i', input_data['video_fp'], output_img_fmt]
        return_result['status'] = subprocess.call(cmd_list)
        output_fn_list = os.listdir(input_data['output_img_dp'])
        output_fn_list.sort()
        current_fn_index = 1.0
        for output_fn in output_fn_list:
            time_seq = float(current_fn_index) * (1000.0 / float(input_data['current_fps']))
            return_result[output_fn] = {'fp': os.path.join(input_data['output_img_dp'], output_fn), 'time_seq': time_seq, 'write_to_file': True, 'in_search_flag': True}
            current_fn_index += 1.0
        return return_result