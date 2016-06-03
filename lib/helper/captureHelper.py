import os
import platform
from ..common.recordscreen import screenshot_capture_line
from ..common.imageTool import ImageTool


def capture_screen(env, output_video_fp, output_img_dp, output_img_name):
    if platform.system().lower() == "windows":
        os.system("ffmpeg -f gdigrab -draw_mouse 0 -framerate 90 -video_size 1024*768 -i desktop -c:v libx264 -preset veryfast  -g 15 -crf 0 -frames 1 " + output_video_fp)
    else:
        os.system(" ".join(screenshot_capture_line(env.DEFAULT_VIDEO_RECORDING_FPS, env.DEFAULT_VIDEO_RECORDING_POS_X,
            env.DEFAULT_VIDEO_RECORDING_POS_Y, env.DEFAULT_VIDEO_RECORDING_WIDTH,
            env.DEFAULT_VIDEO_RECORDING_HEIGHT,
            env.DEFAULT_VIDEO_RECORDING_DISPLAY, env.DEFAULT_VIDEO_RECORDING_CODEC,
            output_video_fp)))

    img_tool_obj = ImageTool()
    img_tool_obj.convert_video_to_images(output_video_fp, output_img_dp, output_img_name)
