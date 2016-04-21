sys.path.append(sys.argv[2])
import browser
import common
import gdoc


com = common.General()
ff = browser.Firefox()
gd = gdoc.gDoc()

ff.clickBar()
ff.enterLink(sys.argv[3])

gd.wait_for_loaded()

for i in range(3):
    wait(0.5)
    type(Key.PAGE_DOWN)

sleep(2)
gd.deFoucsContentWindow()
