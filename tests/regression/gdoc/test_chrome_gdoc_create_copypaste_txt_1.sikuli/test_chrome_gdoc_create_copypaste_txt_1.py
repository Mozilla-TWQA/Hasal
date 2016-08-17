# if you are putting your test script folders under {git project folder}/tests/, it will work fine.
# otherwise, you either add it to system path before you run or hard coded it in here.
sys.path.append(sys.argv[2])
import browser
import common
import gdoc

gd = gdoc.gDoc()
com = common.General()
chrome = browser.Chrome()

chrome.clickBar()
chrome.enterLink(sys.argv[3])
sleep(5)
type("Answer: Depending on how one distinguishes a different Bible version from a revision of an existing Bible version, \
there are as many as 50 different English versions of the Bible. The question then arises: Is there really a need for \
so many different English versions of the Bible? The answer is, of course, no, there is no need for 50 different English \
versions of the Bible. This is especially true considering that there are hundreds of languages into which the entire Bible \
has not yet been translated. At the same time, there is nothing wrong with there being multiple versions of the Bible in a language. \
In fact, multiple versions of the Bible can actually be an aid in understanding the message of the Bible.")
type(Key.ENTER)
type(Key.ENTER)
type("There are two primary reasons for the different English Bible versions. (1) Over time, the English language changes/develops, \
making updates to an English version necessary. If a modern reader were to pick up a 1611 King James Version of the Bible, \
he would find it to be virtually unreadable. Everything from the spelling, to syntax, to grammar, to phraseology is very different. \
Linguists state that the English language has changed more in the past 400 years than the Greek language has changed in the past 2,000 years. \
Several times in church history, believers have gotten ?used? to a particular Bible version and become fiercely loyal to it, \
resisting any attempts to update/revise it. This occurred with the Septuagint, the Latin Vulgate, and more recently, the King James \
Version. Fierce loyalty to a particular version of the Bible is illogical and counterproductive. When the Bible was written, \
it was written in the common language of the people at that time. When the Bible is translated, it should be translated into \
how a people/language group speaks/reads at that time, not how it spoke hundreds of years ago.")
type(Key.ENTER)
com.select_all()
com.cut()
com.paste()
com.paste()

gd.deFoucsContentWindow()