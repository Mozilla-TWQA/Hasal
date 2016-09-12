#!/usr/bin/env python
"""
For Checking environment recording fps capability
"""
import os
import re
import time
import platform
import subprocess
from collections import Counter
from lib.common.environment import Environment
from lib.common.recordscreen import video_capture_line


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
        fps = self.fps_cal()
        assert fps == self.default_fps, "[Error] Your recording fps is: " + str(fps)

    def start_recording(self):
        if os.path.exists(self.video_fn):
            os.remove(self.video_fn)

        if platform.system().lower() == "windows":
            with open(self.recording_log, 'w') as self.fh:
                self.process = subprocess.Popen(
                    "ffmpeg -f gdigrab -draw_mouse 0 -framerate 90 -video_size 1024*768 -i desktop -c:v libx264 -r 90 -preset veryfast -g 15 -crf 0 " + self.env.video_output_fp,
                    stdout=self.fh, stderr=self.fh)
        else:
            vline = video_capture_line(Environment.DEFAULT_VIDEO_RECORDING_FPS,
                                       Environment.DEFAULT_VIDEO_RECORDING_POS_X,
                                       Environment.DEFAULT_VIDEO_RECORDING_POS_Y,
                                       Environment.DEFAULT_VIDEO_RECORDING_WIDTH,
                                       Environment.DEFAULT_VIDEO_RECORDING_HEIGHT,
                                       Environment.DEFAULT_VIDEO_RECORDING_DISPLAY,
                                       Environment.DEFAULT_VIDEO_RECORDING_CODEC, self.video_fn)
            with open(self.recording_log, 'w') as self.fh:
                self.process = subprocess.Popen(vline, stdout=self.fh, stderr=self.fh)

    def stop_recording(self):
        if platform.system().lower() == "windows":
            subprocess.Popen("taskkill /IM ffmpeg.exe /T /F", shell=True)
        else:
            self.process.send_signal(3)
        self.fh.close()

    def fps_cal(self):
        try:
            if os.path.exists(self.recording_log):
                    with open(self.recording_log, 'r') as fh:
                        data = ''.join([line.replace('\n', '') for line in fh.readlines()])
                        fps = map(int, re.findall('fps=(\s\d+\s)', data))
                        count = Counter(fps)
                    fh.close()
                    return count.most_common()[0][0]
            else:
                print("[Error] Recording.log doesn't exist.")
                raise Exception
        except Exception:
            print('[Error] Parsing recording log failed.')
            return None

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
