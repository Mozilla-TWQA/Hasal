__author__ = 'shako'
import os
import cv2
import json
import time
import argparse
import shutil
import numpy as np
from argparse import ArgumentDefaultsHelpFormatter

DEFAULT_IMG_DIR_PATH = os.path.join(os.getcwd(), "images")
DEFAULT_SAMPLE_DIR_PATH = os.path.join(os.getcwd(), "sample")
DEFAULT_IMG_LIST_DATA_FN = "data.json"


class ImageTool(object):

    def __init__(self, **kwargs):
        self.image_list = []
        if "fps" in kwargs:
            self.current_fps = kwargs['fps']
        else:
            self.current_fps = 90

    def dump_result_to_json(self, data, output_fp):
        with open(output_fp, "wb") as fh:
            json.dump(data, fh)

    def convert_video_to_images(self, input_video_fp, output_image_dir_path, output_image_name=None):
        vidcap = cv2.VideoCapture(input_video_fp)
        result, image = vidcap.read()
        if output_image_name:
            if os.path.exists(output_image_dir_path) is False:
                os.mkdir(output_image_dir_path)
            str_image_fp = os.path.join(output_image_dir_path, output_image_name)
            cv2.imwrite(str_image_fp, image)
        else:
            img_cnt = 1
            if os.path.exists(output_image_dir_path):
                shutil.rmtree(output_image_dir_path)
            os.mkdir(output_image_dir_path)
            while result:
                str_image_fp = os.path.join(output_image_dir_path, "image_%d.jpg" % img_cnt)
                cv2.imwrite(str_image_fp, image)
                result, image = vidcap.read()
                img_cnt += 1
                self.image_list.append({"time_seq": vidcap.get(0), "image_fp": str_image_fp})
        return self.image_list

    def compare_with_sample_image(self, input_sample_dp, exec_timestamp_list):
        result_list = []
        print "Comparing sample file start %s" % time.strftime("%c")
        sample_fn_list = os.listdir(input_sample_dp)
        if len(sample_fn_list) != 2:
            return result_list
        sample_fn_list.sort()
        found_1 = False
        found_2 = False
        for sample_fn in sample_fn_list:
            breaking = False
            sample_fp = os.path.join(input_sample_dp, sample_fn)
            sample_dct = self.convert_to_dct(sample_fp)
            # use timestamp to calculate the search index, 5 times of fps is the tolerance
            sample1_search_start_index = int((exec_timestamp_list[1] - exec_timestamp_list[0])*self.current_fps)+int(self.current_fps*5)
            print "current_fps:" + str(self.current_fps)
            print "sample1_search_start_index:" + str(sample1_search_start_index)
            if sample1_search_start_index >= len(self.image_list):
                sample1_search_start_index = len(self.image_list) -1
            print "sample1_search_start_index:" + str(sample1_search_start_index)
            for img_index in range(sample1_search_start_index,1,-1):
                if found_1: break
                image_data = self.image_list[img_index]
                comparing_dct = self.convert_to_dct(image_data['image_fp'])
                if self.compare_two_images(sample_dct, comparing_dct):
                    print "Comparing sample file end %s" % time.strftime("%c")
                    result_list.append(image_data)
                    breaking = True
                    found_1 = True
                    break
            # use timestamp to calculate the search index, 5 times of fps is the tolerance
            sample2_search_start_index = int((exec_timestamp_list[2] - exec_timestamp_list[0])*self.current_fps)-int(self.current_fps*5)
            print "sample2_search_start_index:" + str(sample2_search_start_index)
            if sample2_search_start_index < 0:
                sample2_search_start_index = 0
            print "sample2_search_start_index:" + str(sample2_search_start_index)
            for img_index in range(sample2_search_start_index,len(self.image_list)):
                if breaking: break
                if found_2: break
                image_data = self.image_list[img_index]
                comparing_dct = self.convert_to_dct(image_data['image_fp'])
                if self.compare_two_images(sample_dct, comparing_dct):
                    print "Comparing sample file end %s" % time.strftime("%c")
                    result_list.append(image_data)
                    breaking = True
                    found_2 = True
                    break
        print result_list
        return result_list

    def compare_two_images(self, dct_obj_1, dct_obj_2):
        match = False
        row1, cols1 = dct_obj_1.shape
        row2, cols2 = dct_obj_2.shape
        if (row1 != row2) or (cols1 != cols2):
            return match
        else:
            threshold = 0.0001
            mismatch_rate = np.sum(np.absolute(np.subtract(dct_obj_1,dct_obj_2)))/(row1*cols1)
            if mismatch_rate > threshold:
                return False
            else:
                return True

    def convert_to_dct(self, image_fp):
        img_obj = cv2.imread(image_fp)
        img_gray = cv2.cvtColor(img_obj, cv2.COLOR_BGR2GRAY)
        img_dct = np.float32(img_gray)/255.0
        dct_obj = cv2.dct(img_dct)
        return dct_obj

def main():
    arg_parser = argparse.ArgumentParser(description='Image tool',
                                         formatter_class=ArgumentDefaultsHelpFormatter)
    arg_parser.add_argument('--convertvideo', action='store_true', dest='convert_video_flag', default=False,
                            help='convert video to images.', required=False)
    arg_parser.add_argument('--compareimg', action='store_true', dest='compare_img_flag', default=False,
                            help='compare images.', required=False)
    arg_parser.add_argument('-i', '--input', action='store', dest='input_video_fp', default=None,
                            help='Specify the video file path.', required=False)
    arg_parser.add_argument('-o', '--outputdir', action='store', dest='output_img_dp', default=None,
                            help='Specify output image dir path.', required=False)
    arg_parser.add_argument('-n', '--outputimgname', action='store', dest='output_img_name', default=None,
                            help='Specify output image name.', required=False)
    arg_parser.add_argument('-s', '--sample', action='store', dest='sample_img_dp', default=None,
                            help='Specify sample image dir path.', required=False)
    arg_parser.add_argument('-r', '--resultfp', action='store', dest='result_fp', default=None,
                            help='Specify result file path.', required=False)
    args = arg_parser.parse_args()

    img_tool_obj = ImageTool()
    input_video_fp = args.input_video_fp
    output_img_dp = args.output_img_dp
    output_img_name = args.output_img_name
    sample_img_dp = args.sample_img_dp
    result_fp = args.result_fp

    if args.convert_video_flag is False and args.compare_img_flag is False:
        # default is compare images
        if input_video_fp and output_img_dp and sample_img_dp and result_fp:
            img_tool_obj.convert_video_to_images(input_video_fp, output_img_dp, output_img_name)
            img_tool_obj.dump_result_to_json(img_tool_obj.compare_with_sample_image(sample_img_dp), result_fp)
        else:
            print "Please specify the input video dir path, output image dir path, output image name, sample image dir path and result file path."
    elif args.convert_video_flag:
        # convert video to images
        if input_video_fp and output_img_dp:
            img_tool_obj.convert_video_to_images(input_video_fp, output_img_dp, output_img_name)
        else:
            print "Please specify the input video dir path, output image dir path and output image name."
    else:
        # compare images
        if input_video_fp and output_img_dp and sample_img_dp and result_fp:
            img_tool_obj.convert_video_to_images(input_video_fp, output_img_dp, output_img_name)
            img_tool_obj.dump_result_to_json(img_tool_obj.compare_with_sample_image(sample_img_dp), result_fp)
        else:
            print "Please specify the input video dir path, output image dir path, output image name, sample image dir path and result file path."

if __name__ == '__main__':
    main()