import sys
import platform
from ..common.logConfig import get_logger

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
        logger.info("Move terminal window for Linux.")
        height_offset = 20
        terminal_height = 60

    elif platform_name == 'win32':
        if platform_release == '10':
            logger.info("Move terminal window for Windows 10.")
            height_offset = -4
            terminal_height = 100
        elif platform_release == '7':
            logger.info("Move terminal window for Windows 7.")
            height_offset = 0
            terminal_height = 80
        else:
            logger.info("Move terminal window for Windows.")
            height_offset = 0
            terminal_height = 80

    elif platform_name == 'darwin':
        # TODO: This offset settings only be tested on Mac Book Air
        logger.info("Move terminal window for Mac OSX.")
        height_offset = 25
        terminal_height = 80

    terminal_x = browser_x
    terminal_y = base_height + height_offset

    location = {'x': terminal_x, 'y': terminal_y, 'width': terminal_width, 'height': terminal_height}
    return location
