# Hasal New Agent

## Ejenti Agent

### Usage

```bash
Usage:
  ejenti.py [--cmd-config=<str>] [--job-config=<str>] [--config=<str>]
  ejenti.py (-h | --help)

Options:
  -h --help                       Show this screen.
  --config=<str>                  Specify the config.json file path. [default: configs/ejenti/ejenti_config.json]
  --cmd-config=<str>              Specify the cmd_config.json file path. [default: configs/ejenti/cmd_config.json]
  --job-config=<str>              Specify the job_config.json file path. [default: configs/ejenti/job_config.json]
```

### Configs file

All ejenti configs file are located in `configs/ejenti` folder.

There are `ejenti_config.json`, `cmd_config.json`, and `job_config.json`.

### Modifying the configs

You have to modify the configs file for accessing some services.

For example, you need to modify `job_config.json` to fill the account info, and save as a new file `my_job_config.json`:

```json
{
  "Other Trigger Jobs": "...",

  "listen_pulse": {
    "module-path": "jobs.pulse",
    "trigger-type": "interval",
    "interval": 60,
    "max-instances": 1,
    "default-loaded": true,
    "configs": {
      "username": "<PULSE_ACCOUNT>",
      "password": "<PULSE_PASSWORD>"
    }
  },
  "init_slack_bot": {
    "module-path": "jobs.slack_bot",
    "trigger-type": "interval",
    "interval": 60,
    "max-instances": 1,
    "default-loaded": true,
    "configs": {
      "bot_name": "<SLACK_BOT_NAME>",
      "bot_api_token": "<SLACK_BOT_TOKEN>",
      "bot_mgt_channel": "<SLACK_BOT_MANAGE_CHANNEL>",
      "bot_election_channel": "<SLACK_BOT_ELECTION_CHANNEL>"
    }
  },
  
  "Other Trigger Jobs": "..."
}
```

### Running

Then you can execute the `ejenti` with modified `my_job_config.json`.

Other configs file will be loaded from default configs file.

```bash
$ python ejenti/ejenti.py --job-config PATH/TO/my_job_config.json
```

## Pulse Trigger

### Usage

```bash
Usage:
  pulse_trigger.py [--config=<str>] [--cmd-config=<str>]
  pulse_trigger.py (-h | --help)

Options:
  -h --help                       Show this screen.
  --config=<str>                  Specify the trigger_config.json file path. [default: configs/ejenti/trigger_config.json]
  --cmd-config=<str>              Specify the cmd_config.json file path. [default: configs/ejenti/cmd_config.json]
```

### Configs file

All trigger configs file are located in `configs/ejenti` folder.

There are `trigger_config.json`, and `cmd_config.json`.


### Modifying the configs

You have to modify the configs file for accessing some services.

For example, you need to modify `trigger_config.json` to fill the account info, and save as a new file `my_trigger_config.json`:

```json
{
  "pulse_username": "<PULSE_ACCOUNT>",
  "pulse_password": "<PULSE_PASSWORD>",
  "jobs": {
    "Other Trigger Jobs": "...",
    
    "win10_x64_gmail": {
      "enable": false,
      "topic": "win10",
      "platform_build": "win64",
      "interval_minutes": 1,
      "amount": 3,
      "cmd": "run-hasal-on-latest-nightly",
      "configs": {
        "OVERWRITE_HASAL_SUITE_CASE_LIST": "tests.regression.gmail.test_firefox_gmail_ail_compose_new_mail_via_keyboard,tests.regression.gmail.test_chrome_gmail_ail_compose_new_mail_via_keyboard,tests.regression.gmail.test_firefox_gmail_ail_open_mail,tests.regression.gmail.test_chrome_gmail_ail_open_mail,tests.regression.gmail.test_firefox_gmail_ail_reply_mail,tests.regression.gmail.test_chrome_gmail_ail_reply_mail,tests.regression.gmail.test_firefox_gmail_ail_type_in_reply_field,tests.regression.gmail.test_chrome_gmail_ail_type_in_reply_field",
        "OVERWIRTE_HASAL_CONFIG_CTNT": {
          "configs": {
            "firefox": {
              "obs_on_windows.json": {}
            },
            "index": {
              "inputLatencyAnimationDctGenerator.json": {}
            },
            "upload": {
              "default.json": {
                "enable": true,
                "perfherder-protocol": "https",
                "perfherder-host": "<TREEHERDER_SERVER_HOSTNAME>",
                "perfherder-client-id": "<TREEHERDER_CLIENT_ID>",
                "perfherder-secret": "<TREEHERDER_SECRET_KEY>",
                "perfherder-repo": "<TREEHERDER_REPO>"
              }
            }
          }
        }
      }
    },
    
    "Other Trigger Jobs": "..." 
  },
  "log_filter": [
    "apscheduler.executors.default",
    "apscheduler.scheduler",
    "requests.packages.gurllib3.connectionpool",
    "urllib3.connectionpool"
  ]
}
```

#### The configs description

`topic` should be the Pulse topic. It might be one of `win7`, `win10`, `linux2` or `darwin`.
Please refer to [get_topic()](https://github.com/Mozilla-TWQA/Hasal/blob/master/ejenti/jobs/pulse.py#L36-L54) of `ejenti/jobs/pulse.py`.

`platform_build` should refer to [PLATFORM_FN_MAPPING](https://github.com/Mozilla-TWQA/Hasal/blob/dev/ejenti/tasks/firefoxBuildTasks.py#L18-L22) of `ejenti/tasks/firefoxBuildTasks.py`.

`interval_minutes` will control the checking interval. Trigger will check the file's MD5 base on the platform settings, send the jobs into Pulse if the MD5 is changed.

`amount` will control the jobs amount when it be triggered.

`cmd` is the commands which trigger want ejenti agents to do.

`configs` is the commands configs which trigger will send to ejenti agents with command.

##### The configs of `run-hasal-on-latest-nightly`

`OVERWRITE_HASAL_SUITE_CASE_LIST` will setup the running cases.

`OVERWIRTE_HASAL_CONFIG_CTNT` will setup the Hasal configs parameters. It will base on the folder structure.
For example, 

```json
"configs": {
  "firefox": {
    "obs_on_windows.json": {
      "foo": "bar"
    }
  }
}

```

The above settings will tranfer to `configs/firefox/obs_on_windows.json`, and the value of `foo` will be changed to `bar`.

Keep the object empty when you only want to specify the file without changes.

### Running
```bash
$ python ejenti/pulse_trigger.py --config PATH/TO/my_trigger_config.json
```

### Re-trigger of trigger jobs

You can remove or modify the content of `ejenti/pulse_modules/.md5/<TRIGGER_JOB_NAME>`.

For example, remove the `ejenti/pulse_modules/.md5/win10_x64_gmail` will re-trigger the job `win10_x64_gmail`.

Or you can run `pulse_trigger_cli.py` with your `trigger_config.json`, ex:

```bash
$ python ejenti/pulse_trigger_cli.py --config PATH/TO/trigger_config.json --remove
Job [FOO]: disabled
Job [BAR]: disabled
Job [win10_x64_gmail]: enabled
>>> Remove the checking file of Job [win10_x64_gmail] (y/N): y
    cleaning checking file ...  OK
```
