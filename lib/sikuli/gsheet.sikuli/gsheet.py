from sikuli import *  # NOQA
import common


class gSheet():
    def __init__(self):
        self.common = common.General()
        self.os = str(
            Env.getOS())  # Using Env because of sikuli issue from https://bugs.launchpad.net/sikuli/+bug/1514007

        if self.os.lower() == 'mac':
            self.control = Key.CMD
        else:
            self.control = Key.CTRL
            self.alt = Key.ALT

        self.gsheet_tab_icon = Pattern("pics/gsheet.png").similar(0.70)
        self.gsheet_modify_highlight_cell = Pattern("pics/column_header.png").similar(0.70).targetOffset(450, 180)
        self.gsheet_delete_highlight_cell = Pattern("pics/column_header.png").similar(0.70).targetOffset(450, 180)
        self.gsheet_highlight_tab = Pattern("pics/highlight_tab.png").similar(0.70).targetOffset(160, 0)
        self.gsheet_column_header = Pattern("pics/column_header.png").similar(0.70).targetOffset(0, 60)
        self.gsheet_1st_cell = Pattern("pics/column_header.png").similar(0.70).targetOffset(0, 80)

    def wait_for_loaded(self):
        wait(self.gsheet_tab_icon, 10)

    def modify_highlight_cell(self, input_txt):
        click(self.gsheet_modify_highlight_cell)
        paste(input_txt)

    def delete_highlight_cell(self):
        click(self.gsheet_delete_highlight_cell)
        type(Key.DELETE)

    def delete_all_cell(self):
        type("a", self.control)
        type(Key.DELETE)

    def click_highlight_tab(self):
        click(self.gsheet_highlight_tab)

    def move_to_highlight_scroll(self, input_direction, scroll_down_size):
        if self.os.lower() == 'mac':
            if input_direction == WHEEL_DOWN:
                direction = WHEEL_UP
            else:
                direction = WHEEL_DOWN
        else:
            direction = input_direction
        mouseMove(self.gsheet_column_header)
        wheel(self.gsheet_column_header, direction, scroll_down_size)
