import os
import platform
import subprocess
from ..common.recordscreen import video_capture_line
from base import BaseProfiler


class AvconvProfiler(BaseProfiler):

    process = None

    def start_recording(self):
        if os.path.exists(self.env.video_output_fp):
            os.remove(self.env.video_output_fp)

        if platform.system().lower() == "windows":
            self.process = subprocess.Popen("ffmpeg -f gdigrab -draw_mouse 0 -framerate 1000 -video_size 1024*768 -i desktop -c:v libx264 -preset ultrafast -r 100 " + self.env.video_output_fp)
        else:
		        self.process = subprocess.Popen(
		            video_capture_line(self.env.DEFAULT_VIDEO_RECORDING_FPS, self.env.DEFAULT_VIDEO_RECORDING_POS_X,
		                               self.env.DEFAULT_VIDEO_RECORDING_POS_Y,
		                               self.env.DEFAULT_VIDEO_RECORDING_WIDTH, self.env.DEFAULT_VIDEO_RECORDING_HEIGHT,
		                               self.env.DEFAULT_VIDEO_RECORDING_DISPLAY,
		                               self.env.DEFAULT_VIDEO_RECORDING_CODEC, self.env.video_output_fp))

    def stop_recording(self, **kwargs):
        if platform.system().lower() == "windows":
            subprocess.Popen("taskkill /IM ffmpeg.exe /T /F", shell=True) 
        else:
            self.process.send_signal(3)

