# Tools

Hasal Tools.

Please run following command for installing tools' requirements after activating virtualenv.

**Linux/Mac**

`pip install -r tools/requirements.txt`

or

**Windows**

`conda install --file tools\requirements.txt`

## parse\_hasal\_result

### Prepare

Setup the env:
```bash
$ make clean dev-env
$ source ~/.env-python/bin/activate
(.env-python)$
```

Then running tests. There is the `result.json` file when tests finished.
```bash
$ ls result.json
result.json
```

### Running

Starting parsing the `result.json` file.
Note: you can generate your API key from [HERE](https://bugzilla.mozilla.org/userprefs.cgi?tab=apikey).
```bash
$ python tools/parse_hasal_result.py --input result.json
1) Enter API Key
2) Enter Username and Password
>
```

Typing `y` if you want to file this bug.
```bash
[Bug 1/10]
{
    "product": foo,
    "blocks": [
        foo
    ],
    "description": foo,
    "rep_platform": foo,
    "component": foo,
    "summary": foo,
    "version": foo,
    "op_sys": foo
}
>> Would you want to file the above bug? (y/n)
```

Finally, it will show you all bug list.
```bash
[Submitted Bug List]
Bug 12345 - Foo Bar Baz
Bug 67890 - Foo Bar Baz II

[Skipped Bug List]
Skip - FOO F00 FQQ

[Failed Bug List]
```


# Jupyter

## Input Latency Report Template
report-input-latency.ipynb is designed to generate report for input latency test. Please follow next section to execute ipynb file in shell

## Run jupyter report in shell

```bash
$ for f in *.json ; do file=$f runipy report-input-latency.ipynb report-$f.ipynb; done
```

## Frame Throughput Report Template



