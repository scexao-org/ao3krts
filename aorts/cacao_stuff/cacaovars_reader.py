from __future__ import annotations

import glob
import os
import subprocess
import pathlib
import re
'''
Read environment from a subshell
Stolen from https://stackoverflow.com/questions/1214496/how-to-get-environment-from-a-subprocess
'''


def load_cacao_environment(cacaovars_path: pathlib.Path) -> dict[str, str]:
    '''
        Warning: this performs code execution of the provided file!!

        This function should never have been allowed to exist.
    '''

    assert os.path.isfile(cacaovars_path) and cacaovars_path.is_absolute()

    subproc = subprocess.Popen(
            f'bash -c "source {cacaovars_path} > /dev/null; env"',
            stdout=subprocess.PIPE, shell=True)
    lines = subproc.communicate()[0].decode().split('\n')

    regex_cacao_env = re.compile('^(CACAO_.*)=(.*)$')

    output_env: dict[str, str] = {}

    for line in lines:
        match = re.match(regex_cacao_env, line)
        if match is not None:
            name, val = match.groups()
            output_env[name] = val

    return output_env
