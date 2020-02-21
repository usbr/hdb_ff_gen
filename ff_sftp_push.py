# -*- coding: utf-8 -*-
"""
Created on Fri May 17 09:24:54 2019

@author: buriona
"""
import pysftp
from os import path, remove
import glob
import json

def push_sftp(config_dict, del_local=True, del_remote=True, file_type='*.json'):
    
    if not config_dict:
        return 'Could not push files via sftp, {config_dict} is invalid'
    sftp_config = config_dict['sftp_config']
    local_dir = config_dict['local_path']
    remote_dir = config_dict['remote_path']
    if config_dict['host_keys']:
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys.load(config_dict['host_keys'])
        sftp_config['cnopts'] = cnopts
    if not sftp_config['password']:
        del sftp_config['password']
    else:
        del sftp_config['private_key']
        del sftp_config['private_key_pass']
    
    local_files = glob.glob(path.join(local_dir, file_type), recursive=True)
    num_files = len(local_files)
    results = []
    with pysftp.Connection(**sftp_config) as sftp:
        if del_remote:
            print(f"Cleaning up old files from {sftp_config['host']}")
            old_files = sftp.listdir(remote_dir)
            num_old_files = len(old_files)
            for i, file in enumerate(old_files):
                sftp.remove(f'{remote_dir}/{file}')
                print(f"    Deleted {file} from {sftp_config['host']} {remote_dir} ({i + 1}/{num_old_files})")

        for i, file in enumerate(local_files):
            file = file.replace('\\', '/')
            sftp.chdir(remote_dir)
            try:
                result = sftp.put(file, preserve_mtime=True)
                results.append(result)
                if del_local:
                    remove(file)
                print(f"    Pushed {file} to {sftp_config['host']} {remote_dir} ({i + 1}/{num_files})")
            except Exception as err:
                print(f"    PUSH FAILED: {file} to {sftp_config['host']} {remote_dir} - {err}")
            
    return f"Pushed {len(results)} of {num_files} files to {sftp_config['host']} {remote_dir}"

if __name__ == '__main__':
    this_dir = path.dirname(path.realpath(__file__))
    rise_dir = path.join(this_dir, 'rise')
    config_path = 'sftp_config.json'
    with open(config_path, 'r') as fp:
        sftp_configs = json.load(fp)
    key = 'rise'
    config_dict = sftp_configs[key]   
    scp_push_str = push_sftp(config_dict)
    print(scp_push_str)