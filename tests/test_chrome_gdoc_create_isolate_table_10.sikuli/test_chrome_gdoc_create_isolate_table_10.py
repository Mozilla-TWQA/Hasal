# if you are putting your test script folders under {git project folder}/tests/, it will work fine.
# otherwise, you either add it to system path before you run or hard coded it in here.
sys.path.append(sys.argv[2])

import common
import gdoc

com = common.General()
gd = gdoc.gDoc()
gd.focus_content()
for i in range(10):
    gd.create_table(10,5)
    com.page_end()
    sleep(3)

gd.deFoucsContentWindow()
