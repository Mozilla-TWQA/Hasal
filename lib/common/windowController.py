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
        self.rect = None

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
                self.window_identity = self._get_current_window_id_linux()
            else:
                self.window_identity = self._get_window_id_linux()

    def _get_current_window_id_linux(self):
        cmd = "xprop -root 32x '\t$0' _NET_ACTIVE_WINDOW | cut -f 2"
        cmd_output = subprocess.check_output(cmd, shell=True)
        return cmd_output.strip()

    def _get_window_id_linux(self):
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

    def _move_window_linux2(self):
        if self.window_identity == '0':
            return False
        else:
            mvarg_val = ",".join([str(self.window_gravity), str(self.pos_x), str(self.pos_y), str(self.window_width), str(self.window_height)])
            wmctrl_cmd = " ".join([self.DEFAULT_WMCTRL_CMD, "-i", "-r", self.window_identity, "-e", mvarg_val])
            logger.debug("Move windows command: [%s]" % wmctrl_cmd)
            logger.info('Moving [{}] position ...'.format(self.window_identity_name))
            subprocess.call(wmctrl_cmd, shell=True)
            return True

    def _close_window_linux2(self):
        if self.window_identity == '0':
            return False
        else:
            wmctrl_cmd = ' '.join([self.DEFAULT_WMCTRL_CMD, '-i', '-c', self.window_identity])
            logger.debug('Close windows command: [%s]' % wmctrl_cmd)
            subprocess.call(wmctrl_cmd, shell=True)
            logger.info('Found [{}] and closed the window.'.format(self.window_identity_name))
            return True

    def _move_window_win32_cb(self, hwnd, extra):
        window_title = win32gui.GetWindowText(hwnd)
        for name in self.window_name_list:
            if name in window_title and win32gui.IsWindowVisible(hwnd):
                # move position
                win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, self.pos_x, self.pos_y, self.window_width,
                                      self.window_height, 0)
                self.callback_ret = True
                logger.info('Found [{}] for moving position.'.format(name))
                break

    def _move_window_win32(self):
        # try to move window after window launched
        for counter in range(20):
            win32gui.EnumWindows(self._move_window_win32_cb, None)
            if self.callback_ret:
                self.callback_ret = None
                return True
            time.sleep(1)
        logger.warning('Cannot found one of [{}] for moving position.'.format(self.window_name_list))
        return False

    def _get_window_rect_cb(self, hwnd, extra):
        window_title = win32gui.GetWindowText(hwnd)
        for name in self.window_name_list:
            if name in window_title and win32gui.IsWindowVisible(hwnd):
                logger.info('Found [{}] for get rect.'.format(name))
                self.rect = win32gui.GetWindowRect(hwnd)
                self.callback_ret = True
                break

    def _get_window_rect_win(self):
        # try to get window size after window launched
        for counter in range(20):
            win32gui.EnumWindows(self._get_window_rect_cb, None)
            if self.callback_ret:
                self.callback_ret = None
                return True
            time.sleep(1)
        logger.warning('Cannot found one of [{}] for get rect.'.format(self.window_name_list))
        return False

    def _close_window_win32_cb(self, hwnd, extra):
        window_title = win32gui.GetWindowText(hwnd)
        for name in self.window_name_list:
            if name in window_title:
                # WM_CLOSE = Prompt Confirmation + WM_DESTROY
                # close windows
                win32gui.PostMessage(hwnd, win32con.WM_DESTROY, 0, 0)
                self.callback_ret = True
                logger.info('Found [{}] and closed the window.'.format(name))
                break

    def _close_window_win32(self):
        # try to close window
        for counter in range(10):
            win32gui.EnumWindows(self._close_window_win32_cb, None)
            if self.callback_ret:
                self.callback_ret = None
                return True
            time.sleep(1)
        logger.warning('Cannot found one of [{}] for closing.'.format(self.window_name_list))
        return False

    def _get_window_rect_darwin(self):
        # try to get window size after window launched
        for counter in range(20):
            for app_ref in app('System Events').processes.file.get():
                for name in self.window_name_list:
                    if name in app_ref.name.get():
                        application_obj = app(app_ref.name.get())
                        logger.info('Found [{}] for get rect.'.format(name))
                        for _ in range(10):
                            if application_obj.isrunning():
                                # get window position
                                # Reference: https://www.macosxautomation.com/applescript/firsttutorial/11.html
                                if len(application_obj.windows.bounds.get()) >= 1:
                                    rect = application_obj.windows.bounds.get()[0]
                                    LL = rect[0]
                                    TT = rect[1]
                                    LR = rect[2]
                                    TB = rect[3]
                                    self.rect = [LL, TT, LR - LL, TB - TT]
                                else:
                                    logger.warning('Current list of windows bounds less than 1. [%s]' % application_obj.windows.bounds.get())
                                    return False
                                return True
                            time.sleep(1)
        logger.warning('Cannot found one of [{}] for get rect.'.format(self.window_name_list))
        return False

    def _close_window_darwin(self):
        # try to close window
        for counter in range(10):
            for appname in self.window_name_list:
                try:
                    browser_obj = app(appname)
                    browser_obj.quit()
                    print('Found [{}] and closed the window.'.format(appname))
                    return True
                except:
                    pass
        print('Cannot found one of [{}] for closing.'.format(self.window_name_list))
        return False

    def _move_window_darwin(self):
        # try to move window after window launched
        for counter in range(20):
            for app_ref in app('System Events').processes.file.get():
                for name in self.window_name_list:
                    if name in app_ref.name.get():
                        application_obj = app(app_ref.name.get())
                        logger.info('Found [{}] for moving position.'.format(name))
                        for _ in range(10):
                            if application_obj.isrunning():
                                # move window position
                                # Reference: https://www.macosxautomation.com/applescript/firsttutorial/11.html
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

    def move_window_pos(self, pos_x=None, pos_y=None, window_width=None, window_height=None, window_gravity=None):
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
            return self._move_window_linux2()
        elif self.window_type == 'win32':
            return self._move_window_win32()
        elif self.window_type == 'darwin':
            return self._move_window_darwin()
        else:
            logger.warning('Doesn\'t support moving window [{}] on platform [{}].'.format(self.window_name_list, self.window_type))
            return False

    def get_window_rect(self):
        if self.window_type == 'linux2':
            return False
        elif self.window_type == 'win32':
            return self._get_window_rect_win()
        elif self.window_type == 'darwin':
            return self._get_window_rect_darwin()
        else:
            logger.warning('Doesn\'t support get window rect [{}] on platform [{}].'.format(self.window_name_list,
                                                                                            self.window_type))
            return False

    def close_window(self):
        # Try to move window
        if self.window_type == 'linux2':
            return self._close_window_linux2()
        elif self.window_type == 'win32':
            return self._close_window_win32()
        elif self.window_type == 'darwin':
            return self._close_window_darwin()
        else:
            logger.warning(
                'Doesn\'t support moving window [{}] on platform [{}].'.format(self.window_name_list, self.window_type))
            return False
