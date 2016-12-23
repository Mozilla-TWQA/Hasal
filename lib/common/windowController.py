import time
import sys
import subprocess
from logConfig import get_logger

logger = get_logger(__name__)

if sys.platform == "win32":
    import win32gui
    import win32con
elif sys.platform == "darwin":
    from appscript import *  # NOQA


class WindowObject(object):
    DEFAULT_WMCTRL_CMD = "/usr/bin/wmctrl"

    def __init__(self, input_window_name):
        self.window_type = sys.platform
        self.window_name = input_window_name
        self.window_identity = None

        # default settings
        self.pos_x = 0
        self.pos_y = 0
        self.window_height = 800
        self.window_width = 600
        self.window_gravity = 0

        # get window identity
        self.get_window_identity()

    def get_window_identity(self):
        # the identity only works on Linux now
        if self.window_type == "linux2":
            self.window_identity = self.wmctrl_get_window_id()

    def wmctrl_get_window_id(self):
        window_list_cmd = self.DEFAULT_WMCTRL_CMD + " -l"
        for i in range(10):
            cmd_output = subprocess.check_output(window_list_cmd, shell=True)
            for tmp_line in cmd_output.splitlines():
                tmp_list = tmp_line.split(" ")
                window_title = " ".join(tmp_list[4:])
                if self.window_name in window_title:
                    return tmp_list[0]
            time.sleep(1)
        logger.warning("Can't find window name [%s] in wmctrl list!!!" % self.window_name)
        return "0"

    def wmctrl_move_window(self):
        mvarg_val = ",".join([str(self.window_gravity), str(self.pos_x), str(self.pos_y), str(self.window_width), str(self.window_height)])
        wmctrl_cmd = " ".join([self.DEFAULT_WMCTRL_CMD, "-i", "-r", self.window_identity, "-e", mvarg_val])
        logger.debug("Move windows command: [%s]" % wmctrl_cmd)
        subprocess.call(wmctrl_cmd, shell=True)

    def pywin32_callback_func(self, hwnd, extra):
        # try to move window after window launched
        for counter in range(10):
            window_title = win32gui.GetWindowText(hwnd)
            if self.window_name in window_title:
                win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, self.pos_x, self.pos_y, self.window_width,
                                      self.window_height, 0)
                return True
            time.sleep(1)

    def pywin32_move_window(self):
        win32gui.EnumWindows(self.pywin32_callback_func, None)

    def appscript_move_window(self):
        # try to move window after window launched
        for counter in range(10):
            for app_ref in app('System Events').processes.file.get():
                if self.window_name in app_ref.name.get():
                    application_obj = app(app_ref.name.get())
                    application_obj.windows.bounds.set((self.pos_x, self.pos_y, self.window_width, self.window_height))
                    return True
            time.sleep(1)

    def move_window_pos(self, pos_x, pos_y, window_height, window_width, window_gravity=0):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.window_height = window_height
        self.window_width = window_width
        self.window_gravity = window_gravity
        if self.window_type == 'linux2':
            self.wmctrl_move_window()
        elif self.window_type == 'win32':
            self.pywin32_move_window()
        elif self.window_type == 'darwin':
            self.appscript_move_window()
        else:
            logger.warning('Doesn\'t support moving window [{}] on platform [{}].'.format(self.window_name, self.window_type))
