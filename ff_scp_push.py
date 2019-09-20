# -*- coding: utf-8 -*-
"""
Created on Fri May 17 09:24:54 2019

@author: buriona
"""
import subprocess
from os import path
from datetime import datetime as dt

def push_scp(script_dir=None, script_name='ff_scp_push.txt', scp_path=None):
    if not script_dir:
        script_dir = path.dirname(path.realpath(__file__))
    if not scp_path:
        scp_path = r'C:\Program Files (x86)\WinSCP\winscp.com'
    scp_script_path = path.join(script_dir, script_name)
    if path.isfile(scp_script_path):
        scp_push_process = subprocess.run(
            [scp_path, f'/script={scp_script_path}'],
            shell=True,
            capture_output=True,
            text=True
        )
        if not scp_push_process.returncode:
            scp_push_str = (
                f'\nSuccesfully pushed files to remote using {script_name} - '
                f'@ {dt.now().strftime("%x %X")}'
            )
        else:
            scp_err = scp_push_process.stderr
            scp_push_str = (
                f'ERROR! - Failed to push files to remote via using {script_name} - {scp_err}'
            )

        return scp_push_str

    scp_push_str = (
        f'ERROR! - Could not find sync script {script_name}, failed to push to remote'
    )
    return scp_push_str

if __name__ == '__main__':
    this_dir = path.dirname(path.realpath(__file__))
#    pub_script_name = 'ff_scp_push.txt'
#    push_scp(this_dir, pub_script_name)
    rise_script_name = 'ff_rise_push.txt'
    push_scp(this_dir, rise_script_name)
    result = push_scp(this_dir, )
