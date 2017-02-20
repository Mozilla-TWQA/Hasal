import os
import sys
from ..common.recordscreen import get_mac_os_display_channel
from ..common.imageTool import ImageTool


def capture_screen(env, output_video_fp, output_img_dp, output_img_name):
    if os.path.exists(output_video_fp):
        os.remove(output_video_fp)
    if sys.platform == "win32":
        os.system("ffmpeg -f gdigrab -draw_mouse 0 -framerate " + str(env.DEFAULT_VIDEO_RECORDING_FPS) + " -video_size " + str(env.DEFAULT_VIDEO_RECORDING_WIDTH) + "*" + str(env.DEFAULT_VIDEO_RECORDING_HEIGHT) + " -i desktop -c:v libx264 -preset veryfast  -g 15 -crf 0 -frames 1 " + output_video_fp)
    elif sys.platform == "darwin":
        os.system(
            "ffmpeg -f avfoundation -framerate " + str(env.DEFAULT_VIDEO_RECORDING_FPS) + " -video_size " + str(env.DEFAULT_VIDEO_RECORDING_WIDTH) + "*" + str(env.DEFAULT_VIDEO_RECORDING_HEIGHT) + " -i " + get_mac_os_display_channel() + " -filter:v crop=" + str(env.DEFAULT_VIDEO_RECORDING_WIDTH) + ":" + str(env.DEFAULT_VIDEO_RECORDING_HEIGHT) + ":0:0 -c:v libx264 -preset veryfast  -g 15 -crf 0 -frames 1 " + output_video_fp)
    else:
        os.system(
            "ffmpeg -f x11grab -draw_mouse 0 -framerate " + str(env.DEFAULT_VIDEO_RECORDING_FPS) + " -video_size " + str(env.DEFAULT_VIDEO_RECORDING_WIDTH) + "*" + str(env.DEFAULT_VIDEO_RECORDING_HEIGHT) + " -i " + get_mac_os_display_channel() + " -c:v libx264 -preset veryfast  -g 15 -crf 0 -frames 1 " + output_video_fp)

    img_tool_obj = ImageTool()
    img_tool_obj.convert_video_to_images(output_video_fp, output_img_dp, output_img_name)


def convert_video_to_specify_size(input_video_fp, output_video_fp, resolution_str):
    if os.path.exists(output_video_fp):
        os.remove(output_video_fp)
    cmd_format = "ffmpeg -i %s -s %s %s"
    cmd_str = cmd_format % (input_video_fp, resolution_str, output_video_fp)
    os.system(cmd_str)
