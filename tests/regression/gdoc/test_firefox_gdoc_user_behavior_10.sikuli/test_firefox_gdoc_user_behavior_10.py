# if you are putting your test script folders under {git project folder}/tests/, it will work fine.
# otherwise, you either add it to system path before you run or hard coded it in here.
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
type(Key.ENTER)
type("(2) There are different translation methodologies for how to best render the original Hebrew, Aramaic, and Greek into English. \
Some Bible versions translate as literally (word-for-word) as possible, commonly known as formal equivalence. Some Bible versions \
translate less literally, in more of a thought-for-thought method, commonly known as dynamic equivalence. All of the different English \
Bible versions are at different points of the formal equivalence vs. dynamic equivalence spectrum. The New American Standard Bible \
and the King James Version would be to the far end of the formal equivalence side, while paraphrases such as The Living Bible and \
The Message would be to the far end of the dynamic equivalence side.")
type(Key.ENTER)
type("The advantage of formal equivalence is that it minimizes the translator inserting his/her own interpretations into the passages. \
The disadvantage of formal equivalence is that it often produces a translation so woodenly literal that it is not easily readable/understandable. \
The advantage of dynamic equivalence is that it usually produces a more readable/understandable Bible version. The disadvantage of \
dynamic equivalence is that it sometimes results in ?this is what I think it means? instead of ?this is what it says.? Neither method \
is right or wrong. The best Bible version is likely produced through a balance of the two methodologies.Listed below are the most common \
English versions of the Bible. In choosing which Bible version(s) you are going to use/study, do research, discuss with Christians you respect, \
read the Bibles for yourself, and ultimately, ask God for wisdom regarding which Bible version He desires you to use.")
sleep(1)
for repeat in range(2):
    for i in range(20):
        type(Key.UP)
        sleep(1)

    gd.insert_image_url("https://drive.google.com/open?id=0B9Zi9TqbRWsdTV9JTmZQUXRFTWM")
    sleep(3)

    for i in range(20):
        type(Key.LEFT)
        sleep(1)

    com.select_all()
    sleep(1)
    com.copy()
    sleep(1)
    type(Key.RIGHT)
    sleep(1)
    com.paste()
    sleep(1)

    for i in range(10):
        type(Key.BACKSPACE)
        sleep(1)

    gd.create_table(10,5)
    sleep(1)
    type(Key.UP)
com.paste()
sleep(1)
gd.deFoucsContentWindow()
