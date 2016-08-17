sys.path.append(sys.argv[2])
import browser
import common
import gdoc

com = common.General()
ff = browser.Firefox()
gd = gdoc.gDoc()

ff.clickBar()
ff.enterLink(sys.argv[3])
sleep(5)
gd.wait_for_loaded()

type(Key.END, Key.CTRL)

sleep(2)
gd.deFoucsContentWindow()
