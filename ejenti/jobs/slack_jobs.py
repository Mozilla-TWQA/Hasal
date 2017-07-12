def query_slack_rtm(**kwargs):
    print "async_queue"
    print kwargs['async_queue'].get()
    print "sync_queue"
    print kwargs['sync_queue']


def add_queue(**kwargs):
    kwargs['async_queue'].put("hi")
