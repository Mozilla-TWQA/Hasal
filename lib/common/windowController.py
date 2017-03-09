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

    def __init__(self, input_window_name_list, pos_x=0, pos_y=0, window_width=800, window_height=600, window_gravity=0, current=False):
        self.window_type = sys.platform
        self.window_name_list = input_window_name_list
        self.window_identity = None
        self.window_identity_name = None
        self.callback_ret = None

        # default settings
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.window_width = window_width
        self.window_height = window_height
        self.window_gravity = window_gravity

        # get window identity
        self.get_window_identity(current)

    def get_window_identity(self, current=False):
        # the identity only works on Linux now
        if self.window_type == "linux2":
            if current:
                self.window_identity = self.wmctrl_get_current_window_id()
            else:
                self.window_identity = self.wmctrl_get_window_id()

    def wmctrl_get_current_window_id(self):
        cmd = "xprop -root 32x '\t$0' _NET_ACTIVE_WINDOW | cut -f 2"
        cmd_output = subprocess.check_output(cmd, shell=True)
        return cmd_output.strip()

    def wmctrl_get_window_id(self):
        window_list_cmd = self.DEFAULT_WMCTRL_CMD + " -l"
        for i in range(10):
            cmd_output = subprocess.check_output(window_list_cmd, shell=True)
            logger.debug('Getting window list from wmctrl ...')
            for tmp_line in cmd_output.splitlines():
                tmp_list = tmp_line.split(' ', 4)
                window_id = tmp_list[0]
                window_title = tmp_list[-1]
                logger.debug('Get [{}] in wmctrl'.format(window_title))
                for name in self.window_name_list:
                    if window_title == name or window_title.endswith('- {}'.format(name)):
                        logger.info('Found [{}] in wmctrl list for moving position.'.format(name))
                        self.window_identity_name = name
                        return window_id
            time.sleep(1)
        logger.warning("Can't find one of window name [%s] in wmctrl list!!!" % self.window_name_list)
        return '0'

    def wmctrl_move_window(self):
        if self.window_identity == '0':
            return False
        else:
            mvarg_val = ",".join([str(self.window_gravity), str(self.pos_x), str(self.pos_y), str(self.window_width), str(self.window_height)])
            wmctrl_cmd = " ".join([self.DEFAULT_WMCTRL_CMD, "-i", "-r", self.window_identity, "-e", mvarg_val])
            logger.debug("Move windows command: [%s]" % wmctrl_cmd)
            logger.info('Moving [{}] position ...'.format(self.window_identity_name))
            subprocess.call(wmctrl_cmd, shell=True)
            return True

    def wmctrl_close_window(self):
        if self.window_identity == '0':
            return False
        else:
            wmctrl_cmd = ' '.join([self.DEFAULT_WMCTRL_CMD, '-i', '-c', self.window_identity])
            logger.debug('Close windows command: [%s]' % wmctrl_cmd)
            logger.info('Closing window [{}] ...'.format(self.window_identity_name))
            subprocess.call(wmctrl_cmd, shell=True)
            return True

    def pywin32_callback_func(self, hwnd, extra):
        window_title = win32gui.GetWindowText(hwnd)
        for name in self.window_name_list:
            if name in window_title:
                # move position
                win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, self.pos_x, self.pos_y, self.window_width,
                                      self.window_height, 0)
                self.callback_ret = True
                logger.info('Found [{}] for moving position.'.format(name))
                break

    def pywin32_move_window(self):
        # try to move window after window launched
        for counter in range(10):
            win32gui.EnumWindows(self.pywin32_callback_func, None)
            if self.callback_ret:
                self.callback_ret = None
                return True
            time.sleep(1)
        logger.warning('Cannot found one of [{}] for moving position.'.format(self.window_name_list))
        return False

    def appscript_move_window(self):
        # try to move window after window launched
        for counter in range(10):
            for app_ref in app('System Events').processes.file.get():
                for name in self.window_name_list:
                    if name in app_ref.name.get():
                        application_obj = app(app_ref.name.get())
                        logger.info('Found [{}] for moving position.'.format(name))
                        for _ in range(10):
                            if application_obj.isrunning():
                                # move window position
                                logger.debug('Set bounds of {} to (LL,TT,LR,TB): ({}, {}, {}, {})'
                                             .format(name,
                                                     self.pos_x,
                                                     self.pos_y,
                                                     self.pos_x + self.window_width,
                                                     self.pos_y + self.window_height))
                                application_obj.windows.bounds.set((self.pos_x,
                                                                    self.pos_y,
                                                                    self.pos_x + self.window_width,
                                                                    self.pos_y + self.window_height))
                                # move to foreground by activate it
                                application_obj.activate()
                                return True
                            time.sleep(1)
            time.sleep(1)
        logger.warning('Cannot found one of [{}] for moving position.'.format(self.window_name_list))
        return False

    def move_window_pos(self, pos_x=None, pos_y=None, window_width=None, window_height=None, window_gravity=0):
        if pos_x:
            self.pos_x = pos_x
        if pos_y:
            self.pos_y = pos_y
        if window_width:
            self.window_width = window_width
        if window_height:
            self.window_height = window_height
        if window_gravity:
            self.window_gravity = window_gravity

        # Try to move window
        if self.window_type == 'linux2':
            return self.wmctrl_move_window()
        elif self.window_type == 'win32':
            return self.pywin32_move_window()
        elif self.window_type == 'darwin':
            return self.appscript_move_window()
        else:
            logger.warning('Doesn\'t support moving window [{}] on platform [{}].'.format(self.window_name_list, self.window_type))
            return False
