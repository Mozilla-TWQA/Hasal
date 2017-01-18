sys.path.append(sys.argv[2])
import browser
import common

com = common.General()
ff = browser.Firefox()

wait(2)
ff.focus()
ff.getConsoleInfo("window.performance.timing")

wait(1)
com.dumpToJson(Env.getClipboard(), sys.argv[1])

ff.closeConsole()