__author__ = 'shako'
import os
import platform
import subprocess
from recordscreen import video_capture_line
from recordscreen import screenshot_capture_line
import json


DEFAULT_VIDEO_RECORDING_FPS = 90
DEFAULT_VIDEO_RECORDING_POS_X = 72
DEFAULT_VIDEO_RECORDING_POS_Y = 125
DEFAULT_VIDEO_RECORDING_WIDTH = 1024
DEFAULT_VIDEO_RECORDING_HEIGHT = 768
if platform.system().lower() == "darwin":
    DEFAULT_VIDEO_RECORDING_DISPLAY = "1"
else:
    DEFAULT_VIDEO_RECORDING_DISPLAY = ":0.0+" + str(DEFAULT_VIDEO_RECORDING_POS_X) + "," + str(DEFAULT_VIDEO_RECORDING_POS_X)
DEFAULT_VIDEO_RECORDING_CODEC = "h264_fast"

DEFAULT_CONVERT_VIDEO_TOOL_CMD = "python lib/imageTool.py --convertvideo -i %s -o %s -n %s"
DEFAULT_COMPARING_IMG_TOOL_CMD = "python lib/imageTool.py --compareimg -i %s -o %s -s %s -r %s"

class RecordingVideoObj(object):

    video_recording_process = None

    def start_video_recording(self, output_fp, input_fps=DEFAULT_VIDEO_RECORDING_FPS, input_pos_x=DEFAULT_VIDEO_RECORDING_POS_X,
                              input_pos_y=DEFAULT_VIDEO_RECORDING_POS_Y, input_width=DEFAULT_VIDEO_RECORDING_WIDTH,
                              input_height=DEFAULT_VIDEO_RECORDING_HEIGHT, input_display_device=DEFAULT_VIDEO_RECORDING_DISPLAY,
                              input_codec=DEFAULT_VIDEO_RECORDING_CODEC):

        if os.path.exists(output_fp):
            os.remove(output_fp)

        self.video_recording_process = subprocess.Popen(video_capture_line(input_fps, input_pos_x, input_pos_y,
                                                                           input_width, input_height, input_display_device,
                                                                           input_codec, output_fp))

    def stop_video_recording(self):
        self.video_recording_process.send_signal(3)

    def capture_screen(self, output_video_fp, output_img_dp, output_img_name, input_fps=DEFAULT_VIDEO_RECORDING_FPS, input_pos_x=DEFAULT_VIDEO_RECORDING_POS_X,
                       input_pos_y=DEFAULT_VIDEO_RECORDING_POS_Y, input_width=DEFAULT_VIDEO_RECORDING_WIDTH,
                       input_height=DEFAULT_VIDEO_RECORDING_HEIGHT, input_display_device=DEFAULT_VIDEO_RECORDING_DISPLAY,
                       input_codec=DEFAULT_VIDEO_RECORDING_CODEC):
        os.system(" ".join(screenshot_capture_line(input_fps, input_pos_x, input_pos_y, input_width, input_height,
                                                   input_display_device, input_codec, output_video_fp)))
        os.system(DEFAULT_CONVERT_VIDEO_TOOL_CMD % (output_video_fp, output_img_dp, output_img_name))

class VideoAnalyzeObj(object):

    def run_analyze(self, input_video_fp, output_img_dp, input_sample_dp, result_fp):
        if os.path.exists(output_img_dp) is False:
            os.mkdir(output_img_dp)
        os.system(DEFAULT_COMPARING_IMG_TOOL_CMD % (input_video_fp, output_img_dp, input_sample_dp, result_fp))
        with open(result_fp) as fh:
            result = json.load(fh)
        return result






