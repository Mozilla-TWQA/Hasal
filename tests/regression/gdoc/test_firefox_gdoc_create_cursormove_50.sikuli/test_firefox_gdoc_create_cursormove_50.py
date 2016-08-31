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

for i in range(10):
    com.page_start()
    gd.insert_image_url("https://drive.google.com/open?id=0B9Zi9TqbRWsdTV9JTmZQUXRFTWM")
    sleep(5)
    type("Answer: Depending on how one distinguishes a different Bible version from a revision of an existing Bible version, there are as many as 50 different English versions of the Bible. ")
    type(Key.PAGE_UP)
    com.page_end()
    type("This is especially true considering that there are hundreds of languages into which the entire Bible has not yet been translated. ")
    gd.create_table(20, 5)
    sleep(3)

com.select_all()
com.paste()
com.page_start()
com.paste()

gd.deFoucsContentWindow()
