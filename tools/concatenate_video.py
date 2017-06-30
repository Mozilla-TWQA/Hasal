"""
Usage:
  concatenate_video.py [--top=<str>] [--bottom=<str>] [--left=<str>] [--right=<str>] [--slower-times=<int>]
  concatenate_video.py (-h | --help)

Options:
  -h --help                     Show this screen.
  -t --top=<str>                Specify the folder path of images on video top-half ;[default: ]
  -b --bottom=<str>             Specify the folder path of images on video bottom-half ;[default: ]
  -l --left=<str>               Specify the folder path of images on video left-half ;[default: ]
  -r --right=<str>              Specify the folder path of images on video left-half; [default: ]
  -s --slower-times=<int>       Specify the slower times for customized video; [default: 1]

"""

import os
import cv2
import numpy as np
from docopt import docopt
from lib.common.commonUtil import CommonUtil


class ConcatenateVideo(object):
    def get_img_list(self, img_dp):
        extension_list = ['.jpg', '.bmp', '.png']
        img_list = os.listdir(img_dp)
        img_list = [item for item in img_list if os.path.isfile(os.path.join(img_dp, item)) and os.path.splitext(item)[1] in extension_list]
        img_list.sort(key=CommonUtil.natural_keys)
        img_list = [os.path.join(img_dp, item) for item in img_list]
        return img_list

    def concatenate_video(self, left_img_list, right_img_list, output_video_dp, concatenate_mode, slower_times=1):
        try:
            sample = cv2.imread(left_img_list[0])
            height, width, channel = sample.shape
            video = cv2.VideoWriter()
            fourcc = cv2.cv.FOURCC('m', 'p', '4', 'v')
            video_fp = os.path.join(output_video_dp, 'output.mp4')

            # mode 0 means concatenate top and bottom
            # mode 1 means concatenate left and right
            if concatenate_mode == 0:
                video.open(video_fp, fourcc, 30, (width, height * 2), True)
            elif concatenate_mode == 1:
                video.open(video_fp, fourcc, 30, (width * 2, height), True)
            else:
                raise Exception

            len_firefox = len(left_img_list)
            len_chrome = len(right_img_list)
            vid_len = max(len_firefox, len_chrome)
            for j in range(vid_len):
                if j >= len_firefox:
                    img_left = cv2.imread(left_img_list[len_firefox - 1])
                elif j < len_firefox:
                    img_left = cv2.imread(left_img_list[j])
                if j >= len_chrome:
                    img_right = cv2.imread(right_img_list[len_chrome - 1])
                elif j < len_chrome:
                    img_right = cv2.imread(right_img_list[j])
                for _ in range(slower_times):
                    video.write(np.concatenate((img_left, img_right), axis=concatenate_mode))
            video.release()
        except Exception as e:
            print e
        return True


def main():
    arguments = docopt(__doc__)
    top_img_dp = arguments['--top']
    bottom_img_dp = arguments['--bottom']
    left_img_dp = arguments['--left']
    right_img_dp = arguments['--right']
    slower_times = int(arguments['--slower-times'])

    concatenate_video_obj = ConcatenateVideo()
    if os.path.isdir(top_img_dp) and os.path.isdir(bottom_img_dp):
        concatenate_mode = 0
        top_img_list = concatenate_video_obj.get_img_list(top_img_dp)
        bottom_img_list = concatenate_video_obj.get_img_list(bottom_img_dp)
        concatenate_video_obj.concatenate_video(top_img_list, bottom_img_list, os.getcwd(), concatenate_mode, slower_times)
    elif os.path.isdir(left_img_dp) and os.path.isdir(right_img_dp):
        concatenate_mode = 1
        left_img_list = concatenate_video_obj.get_img_list(left_img_dp)
        right_img_list = concatenate_video_obj.get_img_list(right_img_dp)
        concatenate_video_obj.concatenate_video(left_img_list, right_img_list, os.getcwd(), concatenate_mode, slower_times)
    else:
        print "Please specify two image directory path and corresponding mode to concatenate video."


if __name__ == '__main__':
    main()
