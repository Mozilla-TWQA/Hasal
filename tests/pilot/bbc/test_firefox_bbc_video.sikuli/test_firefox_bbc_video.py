# Go to homepage
wait("firefox_url_bar.png")
paste("firefox_url_bar.png", "http://www.bbc.com/news/video_and_audio/headlines/36957248")
type(Key.ENTER)
wait(20)

current_timeout = getAutoWaitTimeout()
setAutoWaitTimeout(20)

# Wait for video to finish and stop it from continuing
wait("stopVideo.png")
click("stopVideo.png")

setAutoWaitTimeout(current_timeout)
