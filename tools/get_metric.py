import json
import copy
import argparse
from argparse import ArgumentDefaultsHelpFormatter


class ResultMetricGenerator(object):

    def __init__(self, input_result_fp, output_mode=0):
        self.result_fp = input_result_fp
        self.output_mode = int(output_mode)
        self.DEFAULT_SHORT_VIEW_MODE = 0
        self.DEFAULT_EASY_PASTE_MODE = 1
        self.DEFAULT_BROWSER_TYPE_LIST = ['chrome', 'firefox']

    def generate_metric(self):
        DEFAULT_TITLE_LIST = ["CASE NAME", "MEDIAN", "AVG", "STD", "SI", "PSI"]
        DEFAULT_PRINT_KEY_INDEX = ['med_time', 'avg_time', 'std_dev', 'speed_index', 'perceptual_speed_index']
        with open(self.result_fp) as fh:
            obj_json = json.load(fh)

            # generate string format
            if self.output_mode == self.DEFAULT_EASY_PASTE_MODE:
                title_format_str = '{:<50}' + "".join(['\t{:<80}' for i in range(2)])
                content_format_str = '{:<50}' + "".join(['\t{:<15}' for i in range(len(DEFAULT_PRINT_KEY_INDEX)*2)])
            elif self.output_mode == self.DEFAULT_SHORT_VIEW_MODE:
                content_format_str = '{:<50}' + "".join(['\t{:<15}' for i in range(len(DEFAULT_PRINT_KEY_INDEX))])

            # print out title bar
            title_list = copy.deepcopy(DEFAULT_TITLE_LIST)
            if self.output_mode == self.DEFAULT_EASY_PASTE_MODE:
                print(title_format_str.format(*("CASE NAME", "CHROME", "FIREFOX")))
                title_list.extend(title_list[1:])
            print(content_format_str.format(*tuple(title_list)))
            sep_list = ["##############################"]
            sep_list.extend(["###############" for i in range(len(title_list) - 1)])
            print(content_format_str.format(*tuple(sep_list)))

            key_list = copy.deepcopy(obj_json.keys())
            # sort by browser "test_<BROWSER>"_<CASENAME>
            key_list.sort()
            # then sort by case name test_<BROWSER>_"<CASENAME>"
            key_list.sort(key=lambda x: x.split('_', 2)[2])

            handle_data = {}
            browser_type_list = []
            content_list = []
            if self.output_mode == self.DEFAULT_EASY_PASTE_MODE:
                for c_name in key_list:
                    case_name = "_".join(c_name.split("_")[2:])
                    browser_type = c_name.split("_")[1].lower()
                    browser_type_list.append(browser_type)
                    if case_name in handle_data:
                        if browser_type not in handle_data[case_name]:
                            handle_data[case_name][browser_type] = copy.deepcopy(obj_json[c_name])
                    else:
                        handle_data[case_name] = {browser_type: obj_json[c_name]}

                for case_name in handle_data:
                    print_list = [case_name]
                    for b_type in self.DEFAULT_BROWSER_TYPE_LIST:
                        if b_type in handle_data[case_name]:
                            for key in DEFAULT_PRINT_KEY_INDEX:
                                print_list.append(str(handle_data[case_name][b_type].get(key, 'na')))
                        else:
                            for key in DEFAULT_PRINT_KEY_INDEX:
                                print_list.append('na')
                    content_list.append(print_list)
            elif self.output_mode == self.DEFAULT_SHORT_VIEW_MODE:
                for case_name in key_list:
                    print_list = [case_name]
                    for key in DEFAULT_PRINT_KEY_INDEX:
                        print_list.append(str(obj_json[case_name].get(key, 'na')))
                    content_list.append(print_list)

            # print out the result
            for p_data in content_list:
                print(content_format_str.format(*tuple(p_data)))

    def run(self):
        self.generate_metric()


def main():
    arg_parser = argparse.ArgumentParser(description='Result Metric Generator',
                                         formatter_class=ArgumentDefaultsHelpFormatter)
    arg_parser.add_argument('-i', action='store', dest='input_result_fp', default=None,
                            help='specify the file need to parse', required=True)
    arg_parser.add_argument('-m', action='store', dest='output_mode', default=0,
                            help='specify output mode, 1: tab separated, easy copy to sheet, 0: easy for read, shorten version',
                            required=True)
    args = arg_parser.parse_args()
    run_obj = ResultMetricGenerator(args.input_result_fp, args.output_mode)
    run_obj.run()

if __name__ == '__main__':
    main()
