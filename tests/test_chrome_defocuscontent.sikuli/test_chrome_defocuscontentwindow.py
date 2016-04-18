sys.path.append(sys.argv[2])
import browser
import common
import gdoc


com = common.General()
chrome = browser.Chrome()
gd = gdoc.gDoc()

wait(2)
gd.deFoucsContentWindow()
wait(1)