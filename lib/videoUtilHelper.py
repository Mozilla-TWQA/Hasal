__author__ = 'shako'
import os
import platform
import subprocess
from recordscreen import video_capture_line
from videoAnalyzer import VideoAnalyzer
from recordscreen import screenshot_capture_line


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
        video_analyze_obj = VideoAnalyzer()
        video_analyze_obj.convert_video_to_images(output_video_fp, output_img_dp, output_img_name)

class VideoAnalyzeObj(object):

    def run_analyze(self, input_video_fp, output_img_dp, input_sample_dp):
        if os.path.exists(output_img_dp) is False:
            os.mkdir(output_img_dp)
        video_analyze_obj = VideoAnalyzer()
        video_analyze_obj.convert_video_to_images(input_video_fp, output_img_dp)
        return video_analyze_obj.compare_with_sample_image(input_sample_dp)






