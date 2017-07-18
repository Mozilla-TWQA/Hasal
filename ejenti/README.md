# Hasal New Agent

## Running

```bash
$ python ejenti.py
```

The agent can be triggered by a json format configuration file. You need to put the file path in to make sure the agent can be triggered automatically.


## Config

The config file structure:

* config.json
```text
{
  "job_store_url": "sqlite:///job_store.db",
  "interactive_cmd_polling_interval": 5
}
```

* job_config.json
```text
{
  "query_slack_rtm":
  {
    "module-path": "jobs.slack_jobs",
    "trigger-type": "interval",
    "interval": 3,
    "default-loaded": true,
    "configs":{}
  },
  "add_queue": {
    "module-path": "jobs.slack_jobs",
    "trigger-type": "interval",
    "interval": 3,
    "default-loaded": true,
    "configs":{}
  }
}
```

* cmd_config.json
```text
{
  "cmd-settings":
  {
    "add_job": {"desc": "add a existing job from jobstore", "func": "add_func", "queue_type": "async"},
    "del_job": {"desc": "delete a existing job", "func": "del_func", "queue_type": "async"},
    "list_job": {"desc": "list the current jobs", "func": "list_func", "queue_type": "async"},
    "exit": {"desc": "graceful shutdown this agent", "func": "exit_func", "queue_type": "async"}
  }
}
```

