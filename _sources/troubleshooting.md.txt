
# Troubleshooting

This page discusses several possible errors and issues that you might encounter, along with fixes and workarounds.

If you encounter a new issue, suggested resolution, etc., please [submit an Issue](https://github.com/kpwhri/mml_utils/issues/new/choose).


## Metamaplite

### Invalid maximum heap size

#### Error

```shell
Invalid maximum heap size: -Xmx12g
The specified size exceeds the maximum representable size.
Error: Could not create the Java Virtual Machine.
Error: A fatal exception has occurred. Program will exit.
```

#### Explanation

You are running a 32-bit version of Java which has a maximum heap size on Windows around 1.5GB, but Metamaplite is requesting 12GB.

#### Resolution

* Install a 64-bit (`x64`) version of Java (e.g., [Corretto](https://docs.aws.amazon.com/corretto/latest/corretto-8-ug/downloads-list.html)).
* Ensure this version of Java is the first version of Java in your $PATH (check environment variables).
  * This should be done by default.
* Restart any open terminals/powershell to load/refresh the new environment.
