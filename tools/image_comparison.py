"""
Usage:
  img_comp.py [--sample-fp=<str>] [--img-fp=<str>] [--method=<str>]
  img_comp.py (-h | --help)

Options:
  -h --help                     Show this screen.
  --sample-fp=<str>             Specify the sample image's file path ;[default: None]
  --img-fp=<str>                Specify the compared image's file path; [default: None]
  --method=<str>                Specify the comparison method; [default: dct]

"""

import time
from docopt import docopt
from lib.common.imageUtil import convert_to_dct
from lib.common.imageUtil import compare_two_images


def main():
    arguments = docopt(__doc__)
    sample_fp = str(arguments['--sample-fp'])
    img_fp = arguments['--img-fp']
    method = arguments['--method']

    print "########################################################################################################"
    s_time = time.time()
    if method == 'dct':
        _, diff_rate = compare_two_images(convert_to_dct(sample_fp), convert_to_dct(img_fp), 0.005)
        print "The difference rate between sample image and target image from comparison method {method} is " \
              "{diff_rate}.".format(method=method, diff_rate=diff_rate)
    e_time = time.time()
    time_elapsed = e_time - s_time
    print "Compared Elapsed Time: {} seconds".format(time_elapsed)
    print "########################################################################################################"

if __name__ == '__main__':
    main()
