sys.path.append(sys.argv[2])
import browser
import common
import gdoc


com = common.General()
ff = browser.Firefox()
gd = gdoc.gDoc()

ff.clickBar()
ff.enterLink("https://docs.google.com/document/d/1EpYUniwtLvBbZ4ECgT_vwGUfTHKnqSWi7vgNJQBemFk/edit?hl=en")

gd.wait_for_loaded()

for i in range(100):
    wait(0.3)
    type(Key.PAGE_DOWN)
