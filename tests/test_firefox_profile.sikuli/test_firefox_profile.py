sys.path.append(sys.argv[2])
import browser
import common


com = common.General()
ff = browser.Firefox()

wait(2)
ff.focus()
ff.profileAnalyze()

wait(10)
ff.getConsoleInfo("window.tmpProfileBin", "window.Parser.getSerializedProfile(true, function (serializedProfile) { window.tmpProfileBin = serializedProfile; });")

wait(2)
com.dumpToJson(Env.getClipboard(), sys.argv[1])
