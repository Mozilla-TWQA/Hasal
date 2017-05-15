import sys
import platform
from PIL import Image
from lib.common.windowController import WindowObject
from lib.common.logConfig import get_logger

logger = get_logger(__name__)


def get_terminal_location(browser_x, browser_y, browser_w, browser_h):
    """
    Get the terminal location base on browser location.
    @param browser_x: the browser x base.
    @param browser_y: the browser y base.
    @param browser_w: the browser width.
    @param browser_h: the browser height.
    @return: the location of Termianl, {x, y, withd, height}
    """
    platform_name = sys.platform
    platform_release = platform.release()

    base_width = int(browser_x + browser_w)
    base_height = int(browser_y + browser_h)

    height_offset = 0
    terminal_width = base_width
    terminal_height = 60
    if platform_name == 'linux2':
        logger.info('Get terminal window offset for Linux.')
        height_offset = 20
        terminal_height = 60

    elif platform_name == 'win32':
        if platform_release == '10':
            logger.info('Get terminal window offset for Windows 10.')
            height_offset = -4
            terminal_height = 100
        elif platform_release == '7':
            logger.info('Get terminal window offset for Windows 7.')
            height_offset = 0
            terminal_height = 80
        else:
            logger.info('Get terminal window offset for Windows.')
            height_offset = 0
            terminal_height = 80

    elif platform_name == 'darwin':
        # TODO: This offset settings only be tested on Mac Book Air
        logger.info('Get terminal window offset for Mac OSX.')
        height_offset = 25
        terminal_height = 80

    terminal_x = browser_x
    terminal_y = base_height + height_offset

    location = {'x': terminal_x, 'y': terminal_y, 'width': terminal_width, 'height': terminal_height}
    return location


def find_terminal_view(input_file, viewport):
    """
    Find the Region of imageUtil.CropRegion.TERMINAL.
    @param input_file: image file.
    @param viewport: {x, y', width, height} of VIEWPORT.
    @return: {x, y', width, height}
    """
    try:
        im = Image.open(input_file)
        im_width, im_height = im.size

        base_x = int(viewport.get('x', 0))
        base_y = int(viewport.get('y', 0))
        base_width = int(viewport.get('width', im_width))
        base_height = int(viewport.get('height', 0))

        # get Terminal location
        terminal_location = get_terminal_location(base_x, base_y, base_width, base_height)

        """
        The base for cropping is VIEWPORT now, it has the difference y-axis offset from Browser-base.
        Ref:
        `baseTest.py`
        - terminal_location = terminalHelper.get_terminal_location(0, 0, width_browser, height_browser)
        """
        offset_y = 25

        # Adjust the height (do not over the image height)
        terminal_y = terminal_location.get('y')
        bottom = min(im_height, terminal_y + terminal_location.get('height') + offset_y)
        adj_terminal_height = bottom - terminal_y
        terminal_location['height'] = adj_terminal_height

    except Exception as e:
        logger.error(e)
        terminal_location = None
    return terminal_location


def get_terminal_window_object():
    """
    Get the WindowObject, the title will be set base on Platform.
    - darwin: ['Terminal.app', 'iTerm.app']
    - win32: ['runtest.py', 'agent.py', 'cmd', 'Command Prompt', 'python']
    - linux2: ['Hasal']

    Note: The Linux platform will get the handle of current window by "current=True".
    @return: WindowObject of Terminal
    """
    current_platform = sys.platform
    # Get Terminal Window Object here when it still active
    if 'darwin' in current_platform:
        terminal_title = ['Terminal.app', 'iTerm.app']
    elif 'win32' in current_platform:
        terminal_title = ['runtest.py', 'agent.py', 'cmd', 'Command Prompt', 'python']
    elif 'linux2' in current_platform:
        terminal_title = ['Hasal']
    else:
        terminal_title = ['Hasal']

    # Linux will get current by wmctrl_get_current_window_id() method if current is True
    terminal_window_obj = WindowObject(terminal_title, current=True)
    return terminal_window_obj
