# if you are putting your test script folders under {git project folder}/tests/, it will work fine.
# otherwise, you either add it to system path before you run or hard coded it in here.
sys.path.append(sys.argv[2])
import gdoc

gd = gdoc.gDoc()

gd.focus_content()
type("A")
gd.deFoucsContentWindow()
