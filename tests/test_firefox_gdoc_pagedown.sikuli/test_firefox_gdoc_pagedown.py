sys.path.append(sys.argv[2])
import browser
import common


com = common.General()
ff = browser.Firefox()
gd = gdoc.gDoc()

ff.clickBar()
ff.enterLink("https://docs.google.com/document/d/1EpYUniwtLvBbZ4ECgT_vwGUfTHKnqSWi7vgNJQBemFk/edit")

gd.wait_for_loaded()

for i in range(100):
    type(Key.PAGE_DOWN)

wait(6)
ff.getConsoleInfo("window.performance.timing")

wait(1)
com.dumpToJson(Env.getClipboard(), "timing" + sys.argv[1])

