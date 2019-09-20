# -*- coding: utf-8 -*-
"""
Created on Wed May 22 12:08:25 2019

@author: buriona
"""

from shutil import rmtree, copytree
from pathlib import Path

def push_to_tdrive(from_dir, to_dir):
    to_path = Path(to_dir)
    from_path = Path(from_dir)
    rmtree(to_path, ignore_errors=True)
    copytree(from_path, to_path, ignore=True)

if __name__ == '__main__':
    this_dir = Path().absolute()
    data_dir = Path(this_dir, 'flat_files')
