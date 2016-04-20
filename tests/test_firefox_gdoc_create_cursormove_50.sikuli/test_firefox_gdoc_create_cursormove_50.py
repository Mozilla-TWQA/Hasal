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

for i in range(25):
    type("Answer: Depending on how one distinguishes a different Bible version from a revision of an existing Bible version, there are as many as 50 different English versions of the Bible. The question then arises: Is there really a need for so many different English versions of the Bible? The answer is, of course, no, there is no need for 50 different English versions of the Bible.")
    type(Key.PAGE_UP)
    gd.insert_image_url("https://drive.google.com/file/d/0B9Zi9TqbRWsdTV9JTmZQUXRFTWM/view?usp=sharing")
    sleep(5)
    com.page_end()
    type("This is especially true considering that there are hundreds of languages into which the entire Bible has not yet been translated. At the same time, there is nothing wrong with there being multiple versions of the Bible in a language. In fact, multiple versions of the Bible can actually be an aid in understanding the message of the Bible.There are two primary reasons for the different English Bible versions. (1) Over time, the English language changes/develops, making updates to an English version necessary.")
    gd.create_table(10,5)

gd.deFoucsContentWindow()