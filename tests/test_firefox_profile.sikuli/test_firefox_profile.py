sys.path.append(sys.argv[2])
import browser
import common

json_filename = sys.argv[1]

com = common.General()
ff = browser.Firefox()

wait(2)
ff.focus()
url = ff.profileAnalyze()

if url:
    url_filename = '{}_URL.txt'.format(json_filename.rsplit('.', 1)[0])
    com.writeToFile(url, url_filename)

ff.getConsoleInfo("window.tmpProfileBin", "window.Parser.getSerializedProfile(true, function (serializedProfile) { window.tmpProfileBin = serializedProfile; });")

wait(2)
com.dumpToJson(Env.getClipboard(), json_filename)
