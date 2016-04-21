sys.path.append(sys.argv[2])
import browser
import common
import gdoc


com = common.General()
ff = browser.Firefox()
gd = gdoc.gDoc()

ff.clickBar()
ff.enterLink(sys.argv[3])
ff.focus()

gd.wait_for_loaded()

sleep(3)
type(Key.END, Key.CTRL)

sleep(2)
gd.deFoucsContentWindow()
