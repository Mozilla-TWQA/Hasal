# if you are putting your test script folders under {git project folder}/tests/, it will work fine.
# otherwise, you either add it to system path before you run or hard coded it in here.
sys.path.append(sys.argv[2])
import common
import gdoc

com = common.General()
gd = gdoc.gDoc()
gd.focus_content()
for i in range(10):
    gd.insert_image_url("https://drive.google.com/open?id=0B9Zi9TqbRWsdTV9JTmZQUXRFTWM")
    com.page_end()
    sleep(5)

gd.deFoucsContentWindow()
