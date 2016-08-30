#!/usr/bin/env python
"""
Copyright (c) 2014, Google Inc.
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright notice,
      this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright notice,
      this list of conditions and the following disclaimer in the documentation
      and/or other materials provided with the distribution.
    * Neither the name of the company nor the names of its contributors may be
      used to endorse or promote products derived from this software without
      specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."""
import os
import cv2
import json
import copy
import time
import argparse
import shutil
import numpy as np
from argparse import ArgumentDefaultsHelpFormatter
import re
import gc
import math

DEFAULT_IMG_DIR_PATH = os.path.join(os.getcwd(), "images")
DEFAULT_SAMPLE_DIR_PATH = os.path.join(os.getcwd(), "sample")
DEFAULT_IMG_LIST_DATA_FN = "data.json"


class ImageTool(object):

    def __init__(self, fps=0):
        self.image_list = []
        self.current_fps = fps
        self.search_range = [0, 0, 0, 0]

    def dump_result_to_json(self, data, output_fp):
        with open(output_fp, "wb") as fh:
            json.dump(data, fh)

    def convert_video_to_images(self, input_video_fp, output_image_dir_path, output_image_name=None, exec_timestamp_list=[], comp_mode=False):
        vidcap = cv2.VideoCapture(input_video_fp)
        if not self.current_fps:
            if hasattr(cv2, 'CAP_PROP_FPS'):
                self.current_fps = vidcap.get(cv2.CAP_PROP_FPS)
            else:
                self.current_fps = vidcap.get(cv2.cv.CV_CAP_PROP_FPS)
            print '============== FPS from video header: ' + str(self.current_fps) + '==================='
        else:
            print '============== FPS from log file: ' + str(self.current_fps) + '==================='
        result, image = vidcap.read()
        if exec_timestamp_list:
            ref_start_point = exec_timestamp_list[1] - exec_timestamp_list[0]
            ref_end_point = exec_timestamp_list[2] - exec_timestamp_list[0]
            self.search_range = [
                int((ref_start_point - 10) * self.current_fps),
                int((ref_start_point + 10) * self.current_fps),
                int((ref_end_point - 10) * self.current_fps),
                int((ref_end_point + 10) * self.current_fps)]
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
                if (comp_mode and img_cnt >= self.search_range[0] and img_cnt <= self.search_range[3]) or \
                        (img_cnt >= self.search_range[0] and img_cnt <= self.search_range[1]) or \
                        (img_cnt >= self.search_range[2] and img_cnt <= self.search_range[3]) or \
                        not exec_timestamp_list:
                    cv2.imwrite(str_image_fp, image)
                self.image_list.append({"time_seq": vidcap.get(0), "image_fp": str_image_fp})
                result, image = vidcap.read()
                img_cnt += 1
        if self.search_range[0] < 0:
            self.search_range[0] = 0
        if self.search_range[1] > len(self.image_list):
            self.search_range[1] = len(self.image_list)
        if self.search_range[2] < 0:
            self.search_range[2] = 0
        if self.search_range[3] > len(self.image_list):
            self.search_range[3] = len(self.image_list)
        print "Image Comparison search range: " + str(self.search_range)
        return self.image_list

    def compare_with_sample_image(self, input_sample_dp):
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
            for img_index in range(self.search_range[1] - 1, self.search_range[0], -1):
                if found_1: break
                image_data = self.image_list[img_index]
                comparing_dct = self.convert_to_dct(image_data['image_fp'])
                if self.compare_two_images(sample_dct, comparing_dct):
                    print "Comparing sample file end %s" % time.strftime("%c")
                    result_list.append(image_data)
                    breaking = True
                    found_1 = True
                    break
            for img_index in range(self.search_range[2] - 1, self.search_range[3]):
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

    def atoi(self, text):
        return int(text) if text.isdigit() else text

    def natural_keys(self, text):
        return [self.atoi(c) for c in re.split('(\d+)', text)]

    def compare_with_sample_object(self, input_sample_dp):
        result_list = []
        m_start_index = 0
        print "Comparing sample file start %s" % time.strftime("%c")
        sample_fn_list = os.listdir(input_sample_dp)
        if len(sample_fn_list) <= 2:
            return result_list
        sample_fn_list.sort(key=self.natural_keys)
        for sample_index in range(0, len(sample_fn_list)):
            sample_fp = os.path.join(input_sample_dp, sample_fn_list[sample_index])
            if sample_index == 1:
                print "Template matching will skip the second sample's comparison"
            elif sample_index == 0:
                sample_dct = self.convert_to_dct(sample_fp)
                for img_index in range(self.search_range[1] - 1, self.search_range[0], -1):
                    image_data = self.image_list[img_index]
                    comparing_dct = self.convert_to_dct(image_data['image_fp'])
                    if self.compare_two_images(sample_dct, comparing_dct):
                        print "Comparing sample %d file end %s" % (sample_index+1,time.strftime("%c"))
                        result_list.append(image_data)
                        m_start_index = img_index
                        break
            else:
                threshold = 0.00001
                for img_index in range(m_start_index, self.search_range[3]):
                    image_data = self.image_list[img_index]
                    match_val = self.template_match(image_data['image_fp'], sample_fp)
                    if match_val < threshold:
                        result_list.append(image_data)
                        break
                print "Comparing sample %d file end %s" % (sample_index + 1, time.strftime("%c"))
        print result_list
        return result_list

    def template_match(self, base_img_fp, template_fp):
        img = cv2.imread(base_img_fp)
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        template = cv2.imread(template_fp, 0)
        w, h = template.shape[::-1]

        #Choose SQDIFF_NORMED method to perform template matching
        methods = 'cv2.TM_SQDIFF_NORMED'
        method_eval = eval(methods)

        # Apply template Matching
        res = cv2.matchTemplate(img_gray, template, method_eval)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        #For artifactual image output, draw a rectangle on the target object
        str_image_fp = base_img_fp.split('.')[0]+"_TemplateMatch.jpg"
        top_left = min_loc
        bottom_right = (top_left[0] + w, top_left[1] + h)
        cv2.rectangle(img, top_left, bottom_right, (0, 0, 255), 2)
        cv2.imwrite(str_image_fp, img)
        return min_val

    def crop_image(self, input_sample_fp, output_sample_fp, coord=[]):
        img = cv2.imread(input_sample_fp)
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        w, h = img_gray.shape[::-1]
        if not coord or len(coord) != 2 or \
                        type(coord[0]) is not tuple or len(coord[0]) !=2 or \
                        type(coord[1]) is not tuple or len(coord[1]) !=2 :
            coord = [(0,0), (w,h)]
            print "WARNING: Incorrect coordinates, using fully image crop"
        else:
            for i in range(2):
                for j in range(2):
                    new_val = coord[i][j]
                    if coord[i][j] < 0:
                        new_val = 0
                    elif j == 0 and coord[i][j] > w:
                        new_val = w
                    elif j == 1 and coord[i][j] > h:
                        new_val = h
                    if new_val != coord[i][j]:
                        new_xy = [coord[i][0], coord[i][1]]
                        list_index = int(j == 0)
                        new_xy[list_index] = coord[i][list_index]
                        new_xy[j] = new_val
                        coord[i] = tuple(new_xy)
                        print "WARNING: Incorrect coordinates, set %s %s coordinate to %s" % (
                        ["origin", "target"][i], str(unichr(120 + j)), str(new_val))
        print "Crop image range: " + str(coord)
        if coord[0][0] < coord[1][0] and coord[0][1] < coord[1][1]:
            crop_img = img[coord[0][1]:coord[1][1], coord[0][0]:coord[1][0]]
        elif coord[0][0] > coord[1][0] and coord[0][1] > coord[1][1]:
            crop_img = img[coord[1][1]:coord[0][1], coord[1][0]:coord[0][0]]
        elif coord[0][0] < coord[1][0] and coord[0][1] > coord[1][1]:
            crop_img = img[coord[1][1]:coord[0][1], coord[0][0]:coord[1][0]]
        else:
            crop_img = img[coord[0][1]:coord[1][1], coord[1][0]:coord[0][0]]
        cv2.imwrite(output_sample_fp, crop_img)
        return output_sample_fp

    def calculate_progress_for_si(self, result_list):
        histograms = []
        start_index = self.image_list.index(result_list[0])
        end_index = self.image_list.index(result_list[1])
        for i_index in range(start_index, end_index+1, 10):
            image_data = copy.deepcopy(self.image_list[i_index])
            image_data['histogram'] = self.calculate_image_histogram(image_data['image_fp'])
            histograms.append(image_data)
            gc.collect()

        progress = []
        first = histograms[0]['histogram']
        last = histograms[-1]['histogram']
        for index, histogram in enumerate(histograms):
            p = self.calculate_frame_progress(histogram['histogram'], first, last)
            progress.append({'time': histogram['time_seq'],
                             'progress': p,
                             'image_fp': histogram['image_fp']})
        return progress

    def calculate_speed_index(self, progress):
        si = 0
        last_ms = progress[0]['time']
        last_progress = progress[0]['progress']
        for p in progress:
            elapsed = p['time'] - last_ms
            si += elapsed * (1.0 - last_progress)
            last_ms = p['time']
            last_progress = p['progress'] / 100.0
        return int(si)

    def calculate_perceptual_speed_index(self, progress):
        from ssim import compute_ssim
        x = len(progress)
        first_paint_frame = progress[1]['image_fp']
        target_frame = progress[x-1]['image_fp']
        ssim_1 = compute_ssim(first_paint_frame, target_frame)
        per_si = float(progress[1]['time'])
        last_ms = progress[1]['time']
        # Full Path of the Target Frame
        print "Target image for perSI is %s" % target_frame
        ssim = ssim_1
        for p in progress[1:]:
            elapsed = p['time'] - last_ms
            # print '*******elapsed %f'%elapsed
            # Full Path of the Current Frame
            current_frame = p['image_fp']
            print "Current Image is %s" % current_frame
            # Takes full path of PNG frames to compute SSIM value
            per_si += elapsed * (1.0 - ssim)
            ssim = compute_ssim(current_frame, target_frame)
            gc.collect()
            last_ms = p['time']
        return int(per_si)

    def calculate_frame_progress(self, histogram, start, final):
        total = 0
        matched = 0
        slop = 5  # allow for matching slight color variations
        channels = ['r', 'g', 'b']
        for channel in channels:
            channel_total = 0
            channel_matched = 0
            buckets = 256
            available = [0 for i in xrange(buckets)]
            for i in xrange(buckets):
                available[i] = abs(histogram[channel][i] - start[channel][i])
            for i in xrange(buckets):
                target = abs(final[channel][i] - start[channel][i])
                if (target):
                    channel_total += target
                    low = max(0, i - slop)
                    high = min(buckets, i + slop)
                    for j in xrange(low, high):
                        this_match = min(target, available[j])
                        available[j] -= this_match
                        channel_matched += this_match
                        target -= this_match
            total += channel_total
            matched += channel_matched
        progress = (float(matched) / float(total)) if total else 1
        return math.floor(progress * 100)

    def calculate_image_histogram(self, file):
        print 'Calculating histogram for ' + file
        try:
            from PIL import Image

            im = Image.open(file)
            width, height = im.size
            pixels = im.load()
            histogram = {'r': [0 for i in xrange(256)],
                         'g': [0 for i in xrange(256)],
                         'b': [0 for i in xrange(256)]}
            for y in xrange(height):
                for x in xrange(width):
                    try:
                        pixel = pixels[x, y]
                        # Don't include White pixels (with a tiny bit of slop for compression artifacts)
                        if pixel[0] < 250 or pixel[1] < 250 or pixel[2] < 250:
                            histogram['r'][pixel[0]] += 1
                            histogram['g'][pixel[1]] += 1
                            histogram['b'][pixel[2]] += 1
                    except:
                        pass
        except:
            histogram = None
            print 'Error calculating histogram for ' + file
        return histogram


def main():
    arg_parser = argparse.ArgumentParser(description='Image tool',
                                         formatter_class=ArgumentDefaultsHelpFormatter)
    arg_parser.add_argument('--convertvideo', action='store_true', dest='convert_video_flag', default=False,
                            help='convert video to images.', required=False)
    arg_parser.add_argument('--compareimg', action='store_true', dest='compare_img_flag', default=False,
                            help='compare images.', required=False)
    arg_parser.add_argument('--cropimg', action='store_true', dest='crop_img_flag', default=False,
                            help='crop image', required=False)
    arg_parser.add_argument('-i', '--input', action='store', dest='input_video_fp', default=None,
                            help='Specify the file path.', required=False)
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

    if args.crop_img_flag:
        if input_video_fp and output_img_dp and output_img_name:
            if not os.path.exists(output_img_dp):
                os.mkdir(output_img_dp)
            img_tool_obj.crop_image(input_video_fp, os.path.join(output_img_dp,output_img_name))
        else:
            print "Please specify the sample image file path, output image dir path, and output image name."
    elif args.convert_video_flag is False and args.compare_img_flag is False:
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