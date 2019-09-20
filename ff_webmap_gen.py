# -*- coding: utf-8 -*-
"""
Created on Mon May 13 13:45:11 2019

@author: buriona
"""

import os
import pandas as pd

def get_file_list(directory):
    file_list = []
    valid_ext = tuple(['.log', '.csv', '.html', '.json'])
    for root, dirs, files in os.walk(os.path.abspath(directory)):
        for file in files:
            file_list.append(os.path.join(root, file))
    file_list[:] = [f for f in file_list if f.endswith(valid_ext)]
    return file_list

def create_webmap(data_dir, web_prefix=None, isis_prefix=None, csv_name=None):
    if not csv_name:
        csv_name = 'pau_www.usbr.gov_uc_water_ff.csv'

    if not web_prefix:
        web_prefix = 'https://www.usbr.gov/uc/water/ff'

    if not isis_prefix:
        isis_prefix = '/wrg/exec/pub/flat_files'

    local_header = 'file name and location on isis.usbr.gov'
    web_header = 'Posting path URL on www.usbr.gov'

    csv_path = os.path.join(data_dir, csv_name)
    local_file_list = get_file_list(data_dir)
    local_file_list[:] = [i for i in local_file_list if csv_name not in i]

    web_file_list = [
        f.replace(data_dir, web_prefix) for f in local_file_list
    ]
    web_file_list[:] = [f.replace('\\', '/') for f in web_file_list]
    isis_file_list = [
        f.replace(data_dir, isis_prefix) for f in local_file_list
    ]
    isis_file_list[:] = [f.replace('\\', '/') for f in isis_file_list]
    pairs = {
        local_header: isis_file_list,
        web_header: web_file_list
    }

    df = pd.DataFrame.from_dict(pairs)
    df.to_csv(csv_path, index=False)

    return f'Web mapping file - {csv_name} - created.'

if __name__ == '__main__':

    this_dir = os.path.dirname(os.path.realpath(__file__))
    data_dir = os.path.join(this_dir, 'flat_files')
    sys_out = create_webmap(data_dir)
    print(sys_out)
