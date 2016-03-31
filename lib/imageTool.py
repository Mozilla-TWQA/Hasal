__author__ = 'shako'
import os
import cv2
import json
import time
import argparse
import shutil
from argparse import ArgumentDefaultsHelpFormatter

DEFAULT_IMG_DIR_PATH = os.path.join(os.getcwd(), "images")
DEFAULT_SAMPLE_DIR_PATH = os.path.join(os.getcwd(), "sample")
DEFAULT_IMG_LIST_DATA_FN = "data.json"

class ImageTool(object):

    def __init__(self):
        self.image_list = []

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

    def compare_with_sample_image(self, input_sample_dp):
        result_list = []
        print "Comparing sample file start %s" % time.strftime("%c")
        sample_fn_list = os.listdir(input_sample_dp)
        sample_fn_list.sort()
        sample_fn_list.reverse()
        found_flag = False
        search_index = 0
        for sample_fn in sample_fn_list:
            sample_fp = os.path.join(input_sample_dp, sample_fn)
            for img_index in range(len(self.image_list)):
                if found_flag is False:
                    image_data = self.image_list[img_index]
                else:
                    new_index = search_index - img_index
                    image_data = self.image_list[new_index]
                    if new_index < 0:
                        break
                if self.compare_two_images(sample_fp, image_data['image_fp']):
                    print "Comparing sample file end %s" % time.strftime("%c")
                    if found_flag is False:
                        found_flag = True
                        search_index = img_index - 1
                    result_list.append(image_data)
                    if len(result_list) == len(os.listdir(input_sample_dp)):
                        return result_list
                    break
        print "Comparing sample file end %s" % time.strftime("%c")
        return result_list

    def compare_two_images(self, image1_fp, image2_fp):
        match = False
        img1 = cv2.imread(image1_fp)
        img2 = cv2.imread(image2_fp)
        row1, cols1, channel1 = img1.shape
        row2, cols2, channel2 = img2.shape
        if (row1 != row2) or (cols1 != cols2) or (channel1 != channel2):
            return match
        else:
            mismatch = 0
            for i in range(1, row1):
                for j in range(1, cols1):
                    px1 = img1[i, j]
                    px2 = img2[i, j]
                    if max(px1[0],px2[0]) - min(px1[0],px2[0]) > 5 or max(px1[1],px2[1]) - min(px1[1],px2[1]) > 5 or max(px1[2],px2[2]) - min(px1[2],px2[2]) > 5:
                        print "Comparing  sample file [%s] with imgae file [%s] mismatch! value [%s] vs [%s]" % (image1_fp, image2_fp, px1, px2)
                        mismatch += 1
                        return match
            if mismatch == 0:
                match = True
            return match


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
