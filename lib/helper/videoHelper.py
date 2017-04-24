import os
import sys
from ..common.commonUtil import CommonUtil
from ..converter.cv2Converter import Cv2Converter


def capture_screen(env, index_config, output_video_fp, output_img_dp, output_img_name):
    if os.path.exists(output_video_fp):
        os.remove(output_video_fp)
    if sys.platform == "win32":
        os.system("ffmpeg -f gdigrab -draw_mouse 0 -framerate " + str(index_config['video-recording-fps']) + " -video_size " + str(env.DEFAULT_VIDEO_RECORDING_WIDTH) + "*" + str(env.DEFAULT_VIDEO_RECORDING_HEIGHT) + " -i desktop -c:v libx264 -preset veryfast  -g 15 -crf 0 -frames 1 " + output_video_fp)
    elif sys.platform == "darwin":
        os.system(
            "ffmpeg -f avfoundation -framerate " + str(index_config['video-recording-fps']) + " -video_size " + str(env.DEFAULT_VIDEO_RECORDING_WIDTH) + "*" + str(env.DEFAULT_VIDEO_RECORDING_HEIGHT) + " -i " + CommonUtil.get_mac_os_display_channel() + " -filter:v crop=" + str(env.DEFAULT_VIDEO_RECORDING_WIDTH) + ":" + str(env.DEFAULT_VIDEO_RECORDING_HEIGHT) + ":0:0 -c:v libx264 -preset veryfast  -g 15 -crf 0 -frames 1 " + output_video_fp)
    else:
        os.system(
            "ffmpeg -f x11grab -draw_mouse 0 -framerate " + str(index_config['video-recording-fps']) + " -video_size " + str(env.DEFAULT_VIDEO_RECORDING_WIDTH) + "*" + str(env.DEFAULT_VIDEO_RECORDING_HEIGHT) + " -i " + CommonUtil.get_mac_os_display_channel() + " -c:v libx264 -preset veryfast  -g 15 -crf 0 -frames 1 " + output_video_fp)

    input_data = {"video_fp": output_video_fp, "output_img_dp": output_img_dp, "output_image_name": output_img_name}
    cv2_converter_obj = Cv2Converter()
    cv2_converter_obj.generate_result(input_data)


def convert_video_to_specify_size(input_video_fp, output_video_fp, resolution_str):
    if os.path.exists(output_video_fp):
        os.remove(output_video_fp)
    cmd_format = "ffmpeg -i %s -s %s %s"
    cmd_str = cmd_format % (input_video_fp, resolution_str, output_video_fp)
    os.system(cmd_str)
