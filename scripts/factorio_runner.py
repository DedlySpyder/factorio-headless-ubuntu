#!/usr/bin/env python3

import argparse
import subprocess

from pathlib import Path


FACTORIO_EXE = Path('/factorio/bin/x64/factorio')
FACTORIO_LOG_FILE = Path('/factorio/factorio-current.log')

vprint = lambda *_, **__: None


# https://wiki.factorio.com/Command_line_parameters
def run_factorio(*args, fail_on_error=True, verbose=False, executable=str(FACTORIO_EXE)):
    string_args = [str(a) for a in args]
    if verbose:
        print(f'Running Factorio from {executable} with args: {string_args}')
    proc = subprocess.Popen(
        [executable] + string_args,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE
    )

    lines = []
    for line in iter(proc.stdout.readline, None):
        if not line:
            break
        line = line.decode('utf-8')
        lines.append(line)
    proc.stdout.close()
    proc.wait()

    if proc.returncode > 0:
        if fail_on_error:
            print('stderr:')
            print(proc.stderr.read().decode('utf-8'))
            if verbose:
                print('stdout:')
                print(''.join(lines))
            raise RuntimeError('Factorio failed to run')
        else:
            return proc.returncode, proc.stderr.read().decode('utf-8')
    return proc.returncode, lines


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="""Builds the data_raw directory with all prototype data from the local Factorio instance"""
    )

    parser.add_argument('-e', '--executable', action='store', help=f'Factorio exe file to use instead of {FACTORIO_EXE}')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose logging')

    parser.add_argument('factorio_args', action='extend', help='Args to supply to the Factorio executable')

    script_args = parser.parse_args()

    exe = script_args.executable or FACTORIO_EXE
    _, lines = run_factorio(*script_args.factorio_args, verbose=script_args.verbose, executable=exe)

    print(''.join(lines))
