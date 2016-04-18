sys.path.append(sys.argv[2])
import browser
import common


com = common.General()
ff = browser.Firefox()
gd = gdoc.gDoc()

wait(2)
gd.deFoucsContentWindow()
wait(1)