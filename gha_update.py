#!/usr/bin/env python3

import shutil
import subprocess
from os import path
import sys

RASA_ACTIONS_REPO_PATH = '/home/klpanagi/development/dflow-project/rasa-action-server-gha'
GITHUB_USERNAME = 'klpanagi'
GITHUB_TOKEN = ''
BRANCH = 'main'

PIPE = subprocess.PIPE


def update_repo(actions_file_path: str):
    command_a = f'git pull'
    print(f'Executing command: <{command_a}>')
    process = subprocess.Popen(
        command_a,
        stdout=PIPE,
        stderr=PIPE,
        cwd=RASA_ACTIONS_REPO_PATH,
        shell=True
    )
    stdoutput, stderroutput = process.communicate()
    shutil.copyfile(actions_file_path, path.join(RASA_ACTIONS_REPO_PATH,
                                                 'actions', 'actions.py'))
    command_b = 'git add -A .'
    print(f'Executing command: <{command_b}>')
    process = subprocess.Popen(
        command_b,
        stdout=PIPE,
        stderr=PIPE,
        cwd=RASA_ACTIONS_REPO_PATH,
        shell=True
    )
    command_c = 'git commit -m "Updates rasa actions"'
    print(f'Executing command: <{command_c}>')
    process = subprocess.Popen(
        command_c,
        stdout=PIPE,
        stderr=PIPE,
        cwd=RASA_ACTIONS_REPO_PATH,
        shell=True
    )
    stdoutput, stderroutput = process.communicate()

    command_d = f'git push origin {BRANCH}'
    print(f'Executing command: <{command_d}>')
    process = subprocess.Popen(
        command_d,
        stdout=PIPE,
        stderr=PIPE,
        cwd=RASA_ACTIONS_REPO_PATH,
        shell=True
    )
    stdoutput, stderroutput = process.communicate()


if __name__ == '__main__':
    actions_file_path = sys.argv[1]
    update_repo(actions_file_path)
