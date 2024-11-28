# aorts python package

All utilities for the AO RTS23


## This README is trash and was never updated don't read it.


### the datavault subpackage

Supposed to manage and store important configuration files related to and beyond cacao.

Overall will expect the environment variable $DATASTORE_PATH, which will default (`config.py`) to $HOME/datastore.
Layout:
```bash
$DATASTORE_PATH/
    - master_files/ # Not related to a single loop / DM number
        - bim_ttf/
            - bim_ttf_ ...
    - $LOOPNAME-$LOOPNUMBER/
        - <file_type>/
            - <tags>/ # Is this layer necessary?
                - <file_type>_<date>.fits
    - DM-$DMNUMBER/
        - etc...
```

Now naturally, this subpackage contains a TON of entry points, since it's the one used to regenerate ``legacy'' binaries,
such as `update_dm_flat`, `save_flat`, `tt_zero`, `bim_zero`, etc etc.
