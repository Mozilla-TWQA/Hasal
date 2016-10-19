"""
For Checking environment recording fps capability
"""
import os
import time
import platform
import subprocess
from lib.common.environment import Environment
from lib.common.recordscreen import video_capture_line
from lib.common.recordscreen import get_mac_os_display_channel
from lib.helper.resultHelper import fps_cal


class FPSChecker(object):
    def __init__(self):
        self.default_fps = Environment.DEFAULT_VIDEO_RECORDING_FPS
        self.fh = None
        self.process = None
        self.video_fn = "FPSChecker.mkv"
        self.recording_log = "Recording.log"

    def check_recording_fps(self):
        self.start_recording()
        print('[INFO] Screen recording 10 seconds for checking runtime recording fps capability...')
        print('[INFO] Recording fps should match default setting: ' + str(self.default_fps))
        time.sleep(10)
        self.stop_recording()
        time.sleep(3)  # wait for process killed
        status, fps = fps_cal(self.recording_log, self.default_fps)
        assert not int(status), "[Error] Your recording fps is: " + str(fps)

    def start_recording(self):
        if os.path.exists(self.video_fn):
            os.remove(self.video_fn)

        if platform.system().lower() == "windows":
            with open(self.recording_log, 'w') as self.fh:
                self.process = subprocess.Popen(
                    "ffmpeg -f gdigrab -draw_mouse 0 -framerate " + str(self.default_fps) + " -video_size 1024*768 -i desktop -c:v libx264 -r " + str(self.default_fps) + " -preset veryfast -g 15 -crf 0 " + self.video_fn,
                    bufsize=-1, stdout=self.fh, stderr=self.fh)
        else:
            vline = video_capture_line(Environment.DEFAULT_VIDEO_RECORDING_FPS,
                                       Environment.DEFAULT_VIDEO_RECORDING_POS_X,
                                       Environment.DEFAULT_VIDEO_RECORDING_POS_Y,
                                       Environment.DEFAULT_VIDEO_RECORDING_WIDTH,
                                       Environment.DEFAULT_VIDEO_RECORDING_HEIGHT,
                                       get_mac_os_display_channel(),
                                       Environment.DEFAULT_VIDEO_RECORDING_CODEC, self.video_fn)
            self.process = subprocess.Popen(vline, bufsize=-1, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def stop_recording(self):
        if platform.system().lower() == "windows":
            subprocess.Popen("taskkill /IM ffmpeg.exe /T /F", shell=True)
        else:
            self.process.send_signal(3)
            out, err = self.process.communicate()
            with open(self.recording_log, 'w') as self.fh:
                self.fh.write(err)
        self.fh.close()

    def teardown(self):
        if os.path.exists(self.video_fn):
            os.remove(self.video_fn)
        if os.path.exists(self.recording_log):
            os.remove(self.recording_log)


def main():
    try:
        FPSChecker().check_recording_fps()
        print('[INFO] Check recording capability passed.')
        FPSChecker().teardown()
    except Exception as e:
        print(e)
        FPSChecker().teardown()
        exit(1)


if __name__ == '__main__':
    main()
