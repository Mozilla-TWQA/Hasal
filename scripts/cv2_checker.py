#!/usr/bin/env python
"""
For Checking Python CV2 Module
"""

import os
import cv2


class CV2Checker(object):
    def __init__(self):
        self.current_file_dir = os.path.dirname(os.path.realpath(__file__))
        # This video file comes from B2G Gaia repo
        # - https://github.com/mozilla-b2g/gaia/blob/master/test_media/Movies/gizmo2.mp4
        self.input_video = os.path.join(self.current_file_dir, 'media', '168_frame.mp4')
        self.input_video_frame_base = 1

    def check_convert_video_to_images(self):
        video_capture = cv2.VideoCapture(self.input_video)

        ret, _ = video_capture.read()
        counter = 1
        while ret:
            ret, _ = video_capture.read()
            counter += 1
        assert counter > self.input_video_frame_base , 'The video [{}] frame should be more than {}, not {}.'.format(self.input_video, self.input_video_frame_base, counter)


def main():
    try:
        CV2Checker().check_convert_video_to_images()
        print('[INFO] Running python CV2 module passed.')
    except Exception as e:
        print('[Error] Running python CV2 module failed.')
        print(e)
        exit(1)


if __name__ == '__main__':
    main()
