import os
import cv2
import time
import math
import json
import argparse
import peakutils
import numpy as np
from imageTool import ImageTool
from commonUtil import CommonUtil
from argparse import ArgumentDefaultsHelpFormatter
from logConfig import get_logger


logger = get_logger(__name__)


class VideoFluency(object):
    def frame_difference(self, input_image_dir_path):
        """
        Description: calculate the average dct differences between two frames
        Input: a dictionary path to load n images
        Output:
            - differences result for length n-1
            - image file path list for any further usage
        """
        '''
        ======================== *** Not fine-tuned *** ========================
        '''
        difference = []
        img_list = os.listdir(input_image_dir_path)
        img_list.sort(key=CommonUtil.natural_keys)
        img_list = [os.path.join(input_image_dir_path, item) for item in img_list]
        img_list_dct = [ImageTool().convert_to_dct(item) for item in img_list]
        for img_index in range(1, len(img_list)):
            pre_dct = img_list_dct[img_index - 1]
            cur_dct = img_list_dct[img_index]
            mismatch_rate = np.sum(np.absolute(np.subtract(pre_dct, cur_dct))) / (pre_dct.shape[0] * pre_dct.shape[1])
            difference.append(mismatch_rate)
        difference_norm = []
        for i in range(len(difference)):
            norm = difference[i] / max(difference)
            if norm < 0.1:
                difference_norm.append(0)
            else:
                difference_norm.append(norm)
        return difference_norm, img_list

    def moving_average(self, data, n, type='simple'):
        """
        Description: calculate an n period moving average through convolution
                     type is 'simple' | 'exponential'
        Input:
            - data for calculation
            - n period
            - calculation type
        Output: convolution result
        """
        '''
        ======================== *** Not fine-tuned *** ========================
        '''
        data = np.asarray(data)
        if type == 'simple':
            weights = np.ones(n)
        else:
            weights = np.exp(np.linspace(-1., 0., n))

        weights /= weights.sum()

        convolution = np.convolve(data, weights, mode='full')[:len(data)]
        convolution[:n] = convolution[n]
        return convolution

    def similarity(self, first_data, second_data):
        """
        Description: calculate a similarity score through correlation coefficient
        Input: two data sequence to compare
        Output: similarity score between two data sequence
        """
        '''
        ======================== *** Need to find suitable method *** ========================
        '''
        if len(first_data) < len(second_data):
            sim_score = np.corrcoef(np.append(first_data, [0] * (len(second_data) - len(first_data))), second_data)[0][1]
        elif len(first_data) > len(second_data):
            sim_score = np.corrcoef(first_data, np.append(second_data, [0] * (len(first_data) - len(second_data))))[0][1]
        else:
            sim_score = np.corrcoef(first_data, second_data)[0][1]
        return sim_score

    def quantization(self, data):
        """
        Description: transform data to a quantized level
        Input:
            - data sequence to transform
            - number of levels
        Output: normalized data sequence after quantization
        """
        '''
        ======================== *** Not fine-tuned *** ========================
        '''
        level = 16
        Q = (max(data) - min(data)) / level
        data_norm = [round(float(val) / Q) * Q for val in data]
        return data_norm

    def dtw(self, first_data, second_data):
        """
        Description: Dynamic Time Warping(DTW) algorithm allows the computation of
                     optimal alignment between two time series arrays
        Input: two data sequence to calculate
        Output:
            - matrix which contains accumulated distances between two input sequences
            - pure distance matrix between two input sequences
        """
        distance = np.zeros((len(first_data), len(second_data)))
        dtw = np.zeros((len(first_data), len(second_data)))
        dtw[0][0] = np.abs(first_data[0] - second_data[0])
        for i in range(len(first_data)):
            for j in range(len(second_data)):
                cost = np.abs(first_data[i] - second_data[j])
                distance[i][j] = cost
                min_val = 0
                if i and j:
                    min_val = min(dtw[i - 1][j], dtw[i][j - 1], dtw[i - 1][j - 1])
                elif not i and j:
                    min_val = dtw[i][j - 1]
                elif not j and i:
                    min_val = dtw[i - 1][j]
                dtw[i][j] = cost + min_val
        return dtw, distance

    def warp_path(self, dist):
        """
        Description: calculate warp path with minimum cost from a distance matrix
        Input: distance matrix
        Output: warp path which contains pair of coordinates from input matrix
        """
        i = dist.shape[0] - 1
        j = dist.shape[1] - 1
        path = [[i, j]]
        while i > 0 and j > 0:
            if i == 0:
                j = j - 1
            elif j == 0:
                i = i - 1
            else:
                min_val = min(dist[i - 1][j - 1], dist[i - 1][j], dist[i][j - 1])
                if dist[i - 1][j - 1] == min_val:
                    i = i - 1
                    j = j - 1
                elif dist[i - 1][j] == min_val:
                    i = i - 1
                elif dist[i][j - 1] == min_val:
                    j = j - 1
            path.append([i, j])
        path.append([0, 0])
        return path

    def path_cost(self, path, dist):
        """
        Description: calculate the cost of path from a distance matrix
        Input:
            - path from Dynamic Time Warping(DTW)
            - a distance matrix from Dynamic Time Warping(DTW)
        Output: generated video file path list
        """
        cost = 0
        for [map_s, map_f] in path:
            cost = cost + dist[map_s, map_f]
        return cost

    def find_peaks(self, data):
        """
        Description: find index of peaks from data sequence
        Input: a data sequence to calculate
        Output: index list of peaks
        """
        '''
        ======================== *** Not fine-tuned *** ========================
        ======================== *** Need to find suitable method *** ========================
        '''
        threshold = 0.3
        min_dist = 2
        indexes = peakutils.indexes(np.asarray(data), threshold, min_dist)
        return indexes

    def target_peaks(self, path, first_indexes, second_indexes):
        """
        Description: find target peaks and matching based on two peaks location list
        Input:
            - path from Dynamic Time Warping(DTW)
            - peaks location list from two data sequences
        Output: merged target peak location list from two sequences
        """
        '''
        ======================== *** Not fine-tuned *** ========================
        '''
        distance_threshold = 10
        first_peaks = []
        for i in range(len(path)):
            for j in range(len(first_indexes)):
                if (abs((path[i][0] - path[i][1])) > distance_threshold):
                    first_peaks.append(path[i])

        second_peaks = []
        for i in range(len(path)):
            for j in range(len(second_indexes)):
                if (abs((path[i][0] - path[i][1])) > distance_threshold):
                    second_peaks.append(path[i])

        merge_peak = []
        num_peaks = max(len(first_peaks), len(second_peaks))
        for i in range(num_peaks):
            if num_peaks == len(second_peaks):
                merge_peak.append(second_peaks[i])
                if i < len(first_peaks) and not first_peaks[i] in second_peaks:
                    merge_peak.append(first_peaks[i])
            else:
                merge_peak.append(first_peaks[i])
                if i < len(second_peaks) and not second_peaks[i] in first_peaks:
                    merge_peak.append(second_peaks[i])
        merge_peak.sort()
        return merge_peak

    def get_distance(self, peaks):
        return [abs((val[0] - val[1])) for val in peaks]

    def get_average_latency(self, distance):
        return 0.0 if not distance else np.mean(np.array(distance))

    def clustering(self, peaks):
        """
        Description: Clustering matching distance of time between two data sequences
        Input: peak location list from two sequences
        Output: clustering results which contain peak list in each cluster
        """
        '''
        ======================== *** Not fine-tuned *** ========================
        '''
        sequence = []
        v_sequence = []
        if not peaks:
            t_distance_norm = []
        else:
            # cluster_level = 10
            t_distance = self.get_distance(peaks)
            cluster_Q = 200
            t_distance_norm = [math.floor(float(val) / cluster_Q) * cluster_Q for val in t_distance]

            mark_distance = [0] * len(t_distance_norm)
            cur_label = 1
            cur_level = t_distance_norm[0]
            sequence.append(peaks[0])
            mark_distance[0] = cur_label
            for i in range(1, len(mark_distance)):
                if cur_level != t_distance_norm[i]:
                    if cur_level:
                        v_sequence.append(sequence)
                    cur_level = t_distance_norm[i]
                    cur_label += 1
                    sequence = []
                sequence.append(peaks[i])
                mark_distance[i] = cur_label
            v_sequence.append(sequence)
        return v_sequence

    def cluster_duration(self, v_sequence):
        """
        Description: calculate each cluster's start and end points from two data sequences, separately
        Input: clustering results which contain peak list in each cluster
        Output: a list which contains each data sequence's start and end points in every cluster
        """
        '''
        ======================== *** Not fine-tuned *** ========================
        '''
        v_duration = []
        for i in range(len(v_sequence)):
            if i == 0:
                start_point_level = min(v_sequence[i][0]) / 200
                if not start_point_level:
                    start = 0
                else:
                    start = min(v_sequence[i][0]) / 2
                ind_seq1_s = start
                ind_seq2_s = start
                if len(v_sequence) > 1:
                    if (v_sequence[i][len(v_sequence[i]) - 1][0] + 100) >= v_sequence[i + 1][0][0]:
                        ind_seq1_e = v_sequence[i][len(v_sequence[i]) - 1][0] + 1
                    else:
                        ind_seq1_e = v_sequence[i][len(v_sequence[i]) - 1][0] + 200
                    if (v_sequence[i][len(v_sequence[i]) - 1][1] + 100) >= v_sequence[i + 1][0][1]:
                        ind_seq2_e = v_sequence[i][len(v_sequence[i]) - 1][1] + 1
                    else:
                        ind_seq2_e = v_sequence[i][len(v_sequence[i]) - 1][1] + 200
                else:
                    ind_seq1_e = v_sequence[i][len(v_sequence[i]) - 1][0] + 200
                    ind_seq2_e = v_sequence[i][len(v_sequence[i]) - 1][1] + 200
            elif i == (len(v_sequence) - 1):
                seq_len = max(v_sequence[i][len(v_sequence[i]) - 1][0] - v_sequence[i][0][0],
                              v_sequence[i][len(v_sequence[i]) - 1][1] - v_sequence[i][0][1]) + 100
                ind_seq1_s = v_sequence[i][0][0] - seq_len
                ind_seq2_s = v_sequence[i][0][1] - seq_len
                if ind_seq1_s < 0 or ind_seq2_s < 0:
                    compensation = max((0 - ind_seq1_s), (0 - ind_seq2_s))
                    ind_seq1_s += compensation
                    ind_seq2_s += compensation
                ind_seq1_e = v_sequence[i][len(v_sequence[i]) - 1][0] + 200
                ind_seq2_e = v_sequence[i][len(v_sequence[i]) - 1][1] + 200
            else:
                if (v_sequence[i - 1][len(v_sequence[i - 1]) - 1][0] + 100) >= v_sequence[i][0][0]:
                    ind_seq1_s = v_sequence[i - 1][len(v_sequence[i - 1]) - 1][0] + 1
                else:
                    ind_seq1_s = v_sequence[i - 1][len(v_sequence[i - 1]) - 1][0] + 100
                if (v_sequence[i - 1][len(v_sequence[i - 1]) - 1][1] + 100) >= v_sequence[i][0][1]:
                    ind_seq2_s = v_sequence[i - 1][len(v_sequence[i - 1]) - 1][1] + 1
                else:
                    ind_seq2_s = v_sequence[i - 1][len(v_sequence[i - 1]) - 1][1] + 100

                if (v_sequence[i][len(v_sequence[i]) - 1][0] + 100) >= v_sequence[i + 1][0][0]:
                    ind_seq1_e = v_sequence[i + 1][0][0] - 1
                else:
                    ind_seq1_e = v_sequence[i][len(v_sequence[i]) - 1][0] + 100
                if (v_sequence[i][len(v_sequence[i]) - 1][1] + 100) >= v_sequence[i + 1][0][1]:
                    ind_seq2_e = v_sequence[i + 1][0][1] - 1
                else:
                    ind_seq2_e = v_sequence[i][len(v_sequence[i]) - 1][1] + 100
            ind_seq1 = (ind_seq1_s, ind_seq1_e)
            ind_seq2 = (ind_seq2_s, ind_seq2_e)
            v_duration.append([ind_seq1, ind_seq2])
        return v_duration

    def cluster_video_out(self, first_img_list, second_img_list, v_duration, output_video_dp):
        """
        Description: generate video based on each cluster information from two data sequences
        Input:
            - two location list of input images
            - a list which contains each data sequence's start and end points in every cluster
            - the target dictionary of output video
        Output: generated video file path list
        """
        '''
        ======================== *** Not fine-tuned *** ========================
        '''
        video = cv2.VideoWriter()
        if hasattr(cv2, 'VideoWriter_fourcc'):
            fourcc = cv2.VideoWriter_fourcc('X', 'V', 'I', 'D')
        else:
            fourcc = cv2.cv.CV_FOURCC(*'XVID')
        video_list = []
        video_dp = os.path.join(output_video_dp, 'video_fluency_measurement_' + str(int(time.time())))
        if not os.path.exists(video_dp):
            os.mkdir(video_dp)
        for i in range(len(v_duration)):
            video_fp = os.path.join(video_dp, 'video_fluency_measurement_' + str(i + 1) + '.avi')
            video_list.append(video_fp)
            video.open(video_fp, fourcc, 60, (2048, 768), True)
            ind_seq1_s = v_duration[i][0][0]
            ind_seq2_s = v_duration[i][1][0]
            if v_duration[i][0][1] > (len(first_img_list) - 1):
                ind_seq1_e = len(first_img_list) - 1
            else:
                ind_seq1_e = v_duration[i][0][1]
            if v_duration[i][1][1] > (len(second_img_list) - 1):
                ind_seq2_e = len(second_img_list) - 1
            else:
                ind_seq2_e = v_duration[i][1][1]
            seq_len1 = v_duration[i][0][1] - v_duration[i][0][0] + 1
            seq_len2 = v_duration[i][1][1] - v_duration[i][1][0] + 1
            vid_len = max(seq_len1, seq_len2)
            for j in range(vid_len):
                if j >= seq_len1 or (ind_seq1_s + j) >= len(first_img_list):
                    img1 = cv2.imread(first_img_list[ind_seq1_e])
                elif j < seq_len1:
                    img1 = cv2.imread(first_img_list[ind_seq1_s + j])
                if j >= seq_len2 or (ind_seq2_s + j) >= len(second_img_list):
                    img2 = cv2.imread(second_img_list[ind_seq2_e])
                elif j < seq_len2:
                    img2 = cv2.imread(second_img_list[ind_seq2_s + j])
                video.write(np.concatenate((img1, img2), axis=1))
            video.release()
        return video_list


def main():
    arg_parser = argparse.ArgumentParser(description='Video Fluency Measurement',
                                         formatter_class=ArgumentDefaultsHelpFormatter)
    arg_parser.add_argument('-d', '--detection', action='store_true', dest='detection_flag', default=False,
                            help='Detection flag to enable/disable waveform result analysis.', required=False)
    arg_parser.add_argument('-g', '--golden', action='store', dest='golden_img_fp', default=None,
                            help='Specify waveform information file of golden sample.', required=False)
    arg_parser.add_argument('-i', '--input', action='store', dest='input_img_dp', default=None,
                            help='Specify waveform information folder of compared results.', required=False)
    arg_parser.add_argument('-o', '--output_dir', action='store', dest='output_video_dp', default=None,
                            help='Specify output dir path.', required=False)
    arg_parser.add_argument('-v', '--video_enable', action='store', dest='video_out_flag', default=None,
                            help='Output video flag to decide generate video clips or not after analysis.', required=False)
    args = arg_parser.parse_args()

    video_fluency_obj = VideoFluency()
    input_img_dp = args.input_img_dp
    golden_img_dp = args.golden_img_dp
    output_video_dp = args.output_video_dp
    video_out_flag = args.video_out_flag

    time_stamp = str(int(time.time()))
    output_fn = 'video_fluency_measurement_' + time_stamp + '.json'
    output_json_fp = os.path.join(output_video_dp, output_fn)

    with open(golden_img_dp) as fh:
        golden = json.load(fh)
        golden_data = golden['data']
        golden_img_list = golden['img_list']

    if not args.input_img_dp or not args.golden_img_dp:
        logger.error("Please specify golden image dir path and input image dir path.")
    else:
        if os.path.exists(output_json_fp):
            with open(output_json_fp) as fh:
                result = json.load(fh)
        else:
            result = {}
        all_img_dp = os.listdir(input_img_dp)
        all_img_dp = [os.path.join(input_img_dp, item) for item in all_img_dp]
        current_test = os.path.basename(golden_img_dp)
        result[current_test] = {}
        result[current_test]['golden sample'] = golden_img_dp
        result[current_test]['comparison'] = []
        for input_img_dp in all_img_dp:
            with open(input_img_dp) as fh:
                json_input = json.load(fh)
                input_data = json_input['data']
                input_img_list = json_input['img_list']
            comparison_data = {'compared data': input_img_dp,
                               'result clip': None,
                               'latency': 0.0}
            result[current_test]['comparison'].append(comparison_data)
            if args.detection_flag:
                if args.output_video_dp:
                    if not os.path.exists(args.output_video_dp):
                        os.mkdir(args.output_video_dp)
                    threshold = 0.9
                    sim_score = video_fluency_obj.similarity(input_data, golden_data)
                    if sim_score < threshold:
                        d1norm = video_fluency_obj.quantization(golden_data)
                        d2norm = video_fluency_obj.quantization(input_data)
                        dtw, distance = video_fluency_obj.dtw(d1norm, d2norm)
                        path = video_fluency_obj.warp_path(dtw)
                        peak1 = video_fluency_obj.find_peaks(d1norm)
                        peak2 = video_fluency_obj.find_peaks(d2norm)
                        m_peak = video_fluency_obj.target_peaks(path, peak1, peak2)

                        v_sequence = video_fluency_obj.clustering(m_peak)
                        t_distance = video_fluency_obj.get_distance(m_peak)
                        result[current_test]['comparison'][-1]['latency'] = video_fluency_obj.get_average_latency(t_distance)
                        v_duration = video_fluency_obj.cluster_duration(v_sequence)

                        if video_out_flag:
                            video_list = video_fluency_obj.cluster_video_out(golden_img_list, input_img_list, v_duration, output_video_dp)
                            result[current_test]['comparison'][-1]['result clip'] = video_list
                            logger.info(video_list)
                    else:
                        logger.info("Similarity score of input data sequence greater than or equal to threshold")
                else:
                    logger.error("Please specify output video dir path.")
            else:
                print input_img_dp
        latency_list = [item['latency'] for item in result[current_test]['comparison']]
        latency_list.sort()
        non_zero_list = [item for item in latency_list if item != 0]
        if not non_zero_list:
            result[current_test]['average latency'] = 0.0
        else:
            result[current_test]['average latency'] = sum(non_zero_list) / len(non_zero_list)
        result[current_test]['median latency'] = np.median(non_zero_list)
        result[current_test]['occurrence probability'] = float(len(non_zero_list)) / len(latency_list)
        result[current_test]['total comparison'] = len(all_img_dp)
        with open(output_json_fp, "wb") as fh:
            json.dump(result, fh, indent=2)

if __name__ == '__main__':
    main()
