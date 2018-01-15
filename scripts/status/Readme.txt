You need to set task scheduler in windows first:
1. Set up a task to run run.bat
2. Set up a task to "taskkill /IM cmd.exe /T /F" a minute before run run.bat

Make sure your files are correct with your desired settings:
1. obs_on_windows.json
2. InputLatencyAnimationDctGenerator.json
3. suite.txt is with the full set of 30 test cases

The SimpleHTTPServer will be started if run.bat run all the way through.
If it doesn't start up correctly, please do the following command under Hasal folder:
> python -m SimpleHTTPServer 8000
And, then you can connect to http://localhost:8000/scripts/status to see the results

