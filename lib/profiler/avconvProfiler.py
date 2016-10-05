import os
import time
import platform
import subprocess
from ..common.recordscreen import video_capture_line
from ..common.recordscreen import get_mac_os_display_channel
from base import BaseProfiler


class AvconvProfiler(BaseProfiler):

    process = None
    fh = None
    t1_time = None

    def start_recording(self):
        if os.path.exists(self.env.video_output_fp):
            os.remove(self.env.video_output_fp)

        if platform.system().lower() == "windows":
            with open(self.env.recording_log_fp, 'w') as self.fh:
                self.process = subprocess.Popen("ffmpeg -f gdigrab -draw_mouse 0 -framerate " + str(self.env.DEFAULT_VIDEO_RECORDING_FPS) + " -video_size 1024*768 -i desktop -c:v libx264 -r " + str(self.env.DEFAULT_VIDEO_RECORDING_FPS) + " -preset veryfast -g 15 -crf 0 " + self.env.video_output_fp, bufsize=-1, stdout=self.fh, stderr=self.fh)
        else:
            vline = video_capture_line(self.env.DEFAULT_VIDEO_RECORDING_FPS, self.env.DEFAULT_VIDEO_RECORDING_POS_X,
                                       self.env.DEFAULT_VIDEO_RECORDING_POS_Y,
                                       self.env.DEFAULT_VIDEO_RECORDING_WIDTH, self.env.DEFAULT_VIDEO_RECORDING_HEIGHT,
                                       get_mac_os_display_channel(),
                                       self.env.DEFAULT_VIDEO_RECORDING_CODEC, self.env.video_output_fp)
            self.process = subprocess.Popen(vline, bufsize=-1, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

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
            out, err = self.process.communicate()
            with open(self.env.recording_log_fp, 'w') as self.fh:
                self.fh.write(err)
        self.fh.close()
