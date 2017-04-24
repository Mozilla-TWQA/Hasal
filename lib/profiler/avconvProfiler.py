import os
import time
import platform
import subprocess
from ..common.commonUtil import CommonUtil
from base import BaseProfiler


class AvconvProfiler(BaseProfiler):

    def __init__(self, input_env, input_index_config, input_browser_type=None, input_sikuli_obj=None):
        super(AvconvProfiler, self).__init__(input_env, input_index_config, input_browser_type, input_sikuli_obj)
        self.process = None
        self.fh = None
        self.t1_time = None

    def start_recording(self):
        if os.path.exists(self.env.video_output_fp):
            os.remove(self.env.video_output_fp)

        with open(self.env.recording_log_fp, 'w') as self.fh:
            if platform.system().lower() == "windows":
                self.process = subprocess.Popen("ffmpeg -f gdigrab -draw_mouse 0 -framerate " + str(self.input_index_config['video-recording-fps']) + " -video_size " + str(self.env.DEFAULT_VIDEO_RECORDING_WIDTH) + "*" + str(self.env.DEFAULT_VIDEO_RECORDING_HEIGHT) + " -i desktop -c:v libx264 -r " + str(self.input_index_config['video-recording-fps']) + " -preset veryfast -g 15 -crf 0 " + self.env.video_output_fp, bufsize=-1, stdout=self.fh, stderr=self.fh)
            elif platform.system().lower() == "darwin":
                self.process = subprocess.Popen(["ffmpeg", "-f", "avfoundation", "-framerate", str(self.input_index_config['video-recording-fps']), "-video_size", str(self.env.DEFAULT_VIDEO_RECORDING_WIDTH) + "*" + str(self.env.DEFAULT_VIDEO_RECORDING_HEIGHT), "-i", CommonUtil.get_mac_os_display_channel(), "-filter:v", "crop=" + str(self.env.DEFAULT_VIDEO_RECORDING_WIDTH) + ":" + str(self.env.DEFAULT_VIDEO_RECORDING_HEIGHT) + ":0:0", "-c:v", "libx264", "-r", str(self.input_index_config['video-recording-fps']), "-preset", "veryfast", "-g", "15", "-crf", "0", self.env.video_output_fp], bufsize=-1, stdout=self.fh, stderr=self.fh)
            else:
                self.process = subprocess.Popen(["ffmpeg", "-f", "x11grab", "-draw_mouse", "0", "-framerate", str(self.input_index_config['video-recording-fps']), "-video_size", str(self.env.DEFAULT_VIDEO_RECORDING_WIDTH) + "*" + str(self.env.DEFAULT_VIDEO_RECORDING_HEIGHT), "-i", CommonUtil.get_mac_os_display_channel(), "-c:v", "libx264", "-r", str(self.input_index_config['video-recording-fps']), "-preset", "veryfast", "-g", "15", "-crf", "0", self.env.video_output_fp], bufsize=-1, stdout=self.fh, stderr=self.fh)

        for counter in range(10):
            if os.path.exists(self.env.video_output_fp):
                self.t1_time = time.time()
                break
            else:
                time.sleep(0.3)

    def stop_recording(self, **kwargs):
        if platform.system().lower() == "windows":
            subprocess.Popen("taskkill /IM ffmpeg.exe /T /F", shell=True)
        else:
            self.process.send_signal(3)
