# Loopscripts

This folder should package the scripts that usually end up dispatched across the rootdirs. Rather than have them scattered all around the place, maybe this is better?

The various subfolders in this repo are to be symlinked into the various loops as $ROOTDIR / scripts

## A note on pwd

The original scripts were meant to be _located_ and _ran_ from the loop's rootdir. But now they're in `$ROOTDIR/scripts/` (which itself is a symlink to this repo).

This causes mild `pwd` inconveniences. Scripts can be straight up broken, or nest their outputs (e.g. `conf/`) into the `scripts` dir. No good!

To fix this, best to override the `pwd` at the beginning of the scripts. This also unkinks the current directory difference :
```bash
# whether running:
$ROOTDIR/scripts>$ ./this_script
# or:
$ROOTDIR>$ ./scripts/this_script
```

Some cleverness might be better with `cacao-loops` so that the scripts can be deployed from source without static directories (but how to know where a loop that hasn't been re-deployed post-boot is located??), but for now, I guess a simple `cd` should do:

```bash
#!/usr/bin/env bash

# Fix rootdir for nested scripts/ loop scripts!
cd ${HOME}/AOloop/apd3k

...
```
and call all subsequent scripts from the same loop folder as `./scripts/<other_script>`
