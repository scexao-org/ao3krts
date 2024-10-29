from __future__ import annotations

import os, errno
import subprocess
import pathlib
import re
'''
Read environment from a subshell
Stolen from https://stackoverflow.com/questions/1214496/how-to-get-environment-from-a-subprocess
'''

import shlex


def exists(process):
    try:
        os.kill(process.pid, 0)
    except OSError as e:
        return False
    return True


def load_cacao_environment(cacaovars_path: pathlib.Path) -> dict[str, str]:
    '''
        Warning: this performs code execution of the provided file!!

        This function should never have been allowed to exist.
    '''

    assert os.path.isfile(cacaovars_path) and cacaovars_path.is_absolute()

    command = shlex.split(f"bash -c 'source {cacaovars_path} && env'")
    #command = shlex.split(f"bash -c 'ls'")
    subproc = subprocess.Popen(command, stdout=subprocess.PIPE)

    # IT SHOULD SUFFICE TO CALL .poll()
    # https://python-list.python.narkive.com/Q2zUmGKI/trapping-the-segfault-of-a-subprocess-popen
    # Because POpen was segfaulting upon communicate/exit, which is possible if POpen line has silently
    # spawned children of its own
    subproc.wait()

    # Retrieve stdout from bash source
    lines = subproc.communicate()[0].decode().split('\n')

    # Parse environment
    regex_cacao_env = re.compile('^(CACAO_.*)=(.*)$')

    output_env: dict[str, str] = {}

    for line in lines:
        match = re.match(regex_cacao_env, line)
        if match is not None:
            name, val = match.groups()
            output_env[name] = val

    return output_env
