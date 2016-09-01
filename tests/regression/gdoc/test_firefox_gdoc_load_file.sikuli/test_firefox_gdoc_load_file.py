# if you are putting your test script folders under {git project folder}/tests/, it will work fine.
# otherwise, you either add it to system path before you run or hard coded it in here.
# library_path = "/".join(getParentFolder().split("/")[:-2]) + "/lib/sikuli"
# sys.path.append(library_path)
sys.path.append(sys.argv[2])
import browser
import common
import gdoc


com = common.General()
ff = browser.Firefox()
gd = gdoc.gDoc()


ff.clickBar()
ff.enterLink(sys.argv[3])

sleep(2)
gd.deFoucsContentWindow()
