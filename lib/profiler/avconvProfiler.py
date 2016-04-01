import os
import subprocess
from ..common.recordscreen import video_capture_line
from base import BaseProfiler


class AvconvProfiler(BaseProfiler):

    process = None

    def start_recording(self):
        if os.path.exists(self.env.video_output_fp):
            os.remove(self.env.video_output_fp)

        self.process = subprocess.Popen(
            video_capture_line(self.env.DEFAULT_VIDEO_RECORDING_FPS, self.env.DEFAULT_VIDEO_RECORDING_POS_X,
                               self.env.DEFAULT_VIDEO_RECORDING_POS_Y,
                               self.env.DEFAULT_VIDEO_RECORDING_WIDTH, self.env.DEFAULT_VIDEO_RECORDING_HEIGHT,
                               self.env.DEFAULT_VIDEO_RECORDING_DISPLAY,
                               self.env.DEFAULT_VIDEO_RECORDING_CODEC, self.env.video_output_fp))

    def stop_recording(self):
        self.process.send_signal(3)

