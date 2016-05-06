sys.path.append(sys.argv[2])
import browser
import common
import gdoc

com = common.General()
ff = browser.Firefox()
gd = gdoc.gDoc()

wait(2)
ff.focus()
ff.getConsoleInfo("window.performance.timing")

wait(1)
com.dumpToJson(Env.getClipboard(), sys.argv[1])

sleep(2)
gd.deFoucsContentWindow()
