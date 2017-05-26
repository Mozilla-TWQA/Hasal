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

import copy
from commonUtil import CommonUtil
from ..thirdparty.visualmetrics import *  # NOQA
from PIL import Image
from logConfig import get_logger

logger = get_logger(__name__)


def colors_are_similar(a, b, threshold=45):
    similar = True
    sum = 0
    for x in xrange(3):
        delta = abs(a[x] - b[x])
        sum += delta
        if delta > threshold:
            similar = False
    if sum > threshold:
        similar = False

    return similar


def find_tab_view(input_file, viewport):
    """
    Find the Region of imageUtil.CropRegion.TAB_VIEW.
    @param file: image file.
    @param viewport: {x, y', width, height} of VIEWPORT.
    @return: {x, y', width, height}
    """
    try:
        im = Image.open(input_file)
        width, height = im.size
        x = int(math.floor(width / 2))
        y = int(math.floor(viewport['y'] / 2))
        pixels = im.load()
        background = pixels[x, y]

        # Find the top edge
        x = int(math.floor(width / 2))
        top = None
        while top is None and y >= 0:
            if not colors_are_similar(background, pixels[x, y]):
                top = y + 1
            else:
                y -= 1
        if top is None:
            top = 0
        logger.debug('Browser tab view top edge is {0:d}'.format(top))

        # Find the bottom edge
        y = int(math.floor(viewport['y'] / 2))
        bottom = None
        while bottom is None and y < height:
            if not colors_are_similar(background, pixels[x, y]):
                bottom = y - 1
            else:
                y += 1
        if bottom is None:
            bottom = height
        logger.debug('Browser tab view bottom edge is {0:d}'.format(bottom))

        tab_view = {'x': viewport['x'], 'y': top, 'width': viewport['width'], 'height': (bottom - top)}

    except Exception as e:
        tab_view = None
        logger.error(e)

    return tab_view


def calculate_progress_for_si(result_list, input_image_list, frame_calculation_interval=5):
    histograms = []
    start_event_index = 0
    end_event_index = 0

    # convert dict input image list into list order
    image_fn_list = copy.deepcopy(input_image_list.keys())
    image_fn_list.sort(key=CommonUtil.natural_keys)

    for result in result_list:
        if 'start' in result:
            start_event_fp = result['start']
            start_event_fn = os.path.basename(start_event_fp)
            start_event_index = image_fn_list.index(start_event_fn)
        if 'end' in result:
            end_event_fp = result['end']
            end_event_fn = os.path.basename(end_event_fp)
            end_event_index = image_fn_list.index(end_event_fn)

    # The current algorithm is to calculate the histogram of 5 frames per time, so the allowance would be within 5 frames
    # Might need to adjust if we need to raise the accuracy
    for i_index in range(start_event_index, end_event_index + 1, frame_calculation_interval):
        image_fn = image_fn_list[i_index]
        image_data = copy.deepcopy(input_image_list[image_fn])
        image_data['histogram'] = calculate_image_histogram(image_data['viewport'])
        histograms.append(image_data)
        gc.collect()

    if end_event_index % frame_calculation_interval:
        end_image_data = copy.deepcopy(input_image_list[end_event_fn])
        end_image_data['histogram'] = calculate_image_histogram(end_image_data['viewport'])
        histograms.append(end_image_data)
        gc.collect()

    progress = []
    first = histograms[0]['histogram']
    last = histograms[-1]['histogram']
    for index, histogram in enumerate(histograms):
        p = calculate_frame_progress(histogram['histogram'], first, last)
        progress.append({'time': histogram['time_seq'],
                         'progress': p,
                         'image_fp': histogram['viewport']})
    return progress


def calculate_perceptual_speed_index(progress):
    from ssim import compute_ssim
    x = len(progress)
    target_frame = progress[x - 1]['image_fp']
    per_si = 0.0
    last_ms = progress[0]['time']
    # Full Path of the Target Frame
    logger.info("Target image for perSI is %s" % target_frame)
    for p in progress:
        elapsed = p['time'] - last_ms
        # print '*******elapsed %f'%elapsed
        # Full Path of the Current Frame
        current_frame = p['image_fp']
        # Takes full path of PNG frames to compute SSIM value
        ssim = compute_ssim(current_frame, target_frame)
        per_si += elapsed * (1.0 - ssim)
        gc.collect()
        last_ms = p['time']
    return int(per_si)


def find_image_viewport(file):
    """
    Find the Region of imageUtil.CropRegion.VIEWPORT.
    @param file: image file.
    @return: {x, y', width, height}
    """
    try:
        im = Image.open(file)
        width, height = im.size
        x = int(math.floor(width / 4))
        y = int(math.floor(height / 4))
        pixels = im.load()
        white_rgb = (255, 255, 255)
        # based on needs, set white color as target background
        background = white_rgb

        # Find the left edge
        left = None
        while left is None and x >= 0:
            if not colors_are_similar(background, pixels[x, y]):
                left = x + 1
            else:
                x -= 1
        if left is None:
            left = 0
        logger.debug('Viewport left edge is {0:d}'.format(left))

        # Find the right edge
        x = int(math.floor(width / 2))
        right = None
        while right is None and x < width:
            if not colors_are_similar(background, pixels[x, y]):
                right = x - 1
            else:
                x += 1
        if right is None:
            right = width
        logger.debug('Viewport right edge is {0:d}'.format(right))

        # Find the top edge
        x = int(math.floor(width / 2))
        top = None
        while top is None and y >= 0:
            if not colors_are_similar(background, pixels[x, y]):
                top = y + 1
            else:
                y -= 1
        if top is None:
            top = 0
        logger.debug('Viewport top edge is {0:d}'.format(top))

        # Find the bottom edge
        y = int(math.floor(height / 2))
        bottom = None
        while bottom is None and y < height:
            if not colors_are_similar(background, pixels[x, y]):
                bottom = y - 1
            else:
                y += 1
        if bottom is None:
            bottom = height
        logger.debug('Viewport bottom edge is {0:d}'.format(bottom))

        viewport = {'x': left, 'y': top, 'width': (right - left), 'height': (bottom - top)}
    except Exception as e:
        logging.debug(e)
        viewport = None

    return viewport
