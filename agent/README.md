# Hasal Online Agent

## Running

```bash
$ python agent.py --dirpath <CONFIG DIR PATH>
```

The agent can be triggered by a json format configuration file. You need to put the file path in to make sure the agent can be triggered automatically.


## Config

The config file structure:

```text
{
    "JOB_NAME": "JOB_NAME",             # Optional, the agent task name, [default: "Jenkins Job"]
    "interval": 30,                     # Optional, the interval of agent monitoring config dir [default: 30]
    "AGENT_MODULE_PATH": "hasaltask",   # Optional, the module file name will be loaded in to agent task [default: hasaltask]
    "AGENT_OBJECT_NAME": "HasalTask"    # Optional, the module class name will be loaded in to agent task [default: HasalTask]
}
```
