# Hasal Online Server

## Running

By default, the config files will be put under `~/.hasal_server` folder.

```bash
$ pushd server
$ python server.py <IP>:<PORT>
  ...
$ popd
```

If you want to run it with customized config, please set your path to environment variable `CONFIG_PATH`.

```bash
$ pushd server
$ CONFIG_PATH=~/.hasal_server_try python server.py <IP>:<PORT>
  ...
$ popd
```

## Config

The config file structure:

```text
{
    "test_times": 30,                       # The testing times for calculating the median, avg, and so on.
    "perfherder_protocol": "http",          # The following "perfherder-*" settings are defined for local Treeherder.
    "perfherder_host": "local.treeherder.mozilla.org",
    "perfherder_client_id": "",
    "perfherder_secret": "",
    "perfherder_repo": "mozilla-central",
    "dashboard_host": "",                   # TBD
    "dashboard_ssh": ""                     # TBD
}
```
