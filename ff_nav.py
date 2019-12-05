# -*- coding: utf-8 -*-
"""
Created on Thu May  2 06:33:43 2019

@author: buriona
"""

import os
from functools import reduce
from datetime import datetime as dt
from pathlib import Path
import pandas as pd
from ff_dash import create_dash
from ff_utils import get_favicon, get_bor_seal, get_bootstrap

BOR_FLAVICON = get_favicon()
BOR_SEAL = get_bor_seal()
bootstrap = get_bootstrap()
BOOTSTRAP_CSS = bootstrap['css']
BOOTSTRAP_JS = bootstrap['js']
JQUERY_JS = bootstrap['jquery']
POPPER_JS = bootstrap['popper']
HEADER_STR = f'''
<!DOCTYPE html>
<html>
    <head>
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <link rel="icon" href="{BOR_FLAVICON}">
          <link rel="stylesheet" href="{BOOTSTRAP_CSS}">
          <script src="{JQUERY_JS}"></script>
          <script src="{BOOTSTRAP_JS}"></script>
          <script src="{POPPER_JS}"></script>''' + '''
    <style>
        .dropdown-submenu {
          position: relative;
        }

        .dropdown-submenu .dropdown-menu {
          top: 0;
          left: 100%;
          margin-top: -1px;
        }
    </style>
    </head>
<body>
<div class="container">
''' + f'''
<img src="{BOR_SEAL}" style="width: 25%" class="img-responsive mx-auto d-block" alt="BOR Logo">
    <h2>HDB Flat File Navigator</h2>
'''

FOOTER_STR = '''
<a href="./ff_gen.log" class="btn btn-success mt-3" role="button">LOG FILE</a>
</div>
<script>
$(document).ready(function(){
  $('.dropdown-submenu a.test').on("click", function(e){
    $(this).next('ul').toggle();
    e.stopPropagation();
    e.preventDefault();
  });
});

</script>

</body>
</html>
'''

def get_updt_str():
    return f'<i>Last updated: {dt.now().strftime("%x %X")}</i>'

def remove_items(key_list, items_dict):
    for key in key_list:
        items_dict.pop(key, None)
    return items_dict

def write_file(write_dict):
    for filepath, html_str in write_dict.items():
        with open(filepath, 'w') as file:
            file.write(html_str)

def create_chart_dd(button_label, site_id, charts, data_dir):
    chart_href = Path(data_dir, button_label, site_id, 'charts')
    chart_menu_dict = {}
    for chart_name, chart_none in charts.items():
        chart_label = chart_name.replace('.html', '')
        chart_label = chart_label.upper().replace('_', ' ')
        site_chart_href = Path(chart_href, chart_name)
        chart_menu_dict[chart_label] = site_chart_href

    charts_dd = get_sub_menus(
        'CHARTS',
        chart_href,
        chart_menu_dict,
        sub_menu_dd=''
    )

    return charts_dd

def create_data_dd(button_label, site_id, data, data_dir, meta, data_format):
    data_href = Path(data_dir, button_label, site_id, data_format)
    data_menu_dict = {}
    for data_name, data_none in data.items():
        data_id = int(data_name.replace(f'.{data_format}', ''))
        data_label = get_datatype_name(
            data_id,
            meta
        )
        data_label = str(data_label).upper()
        site_data_dd_href = Path(data_href, data_name)
        data_menu_dict[data_label] = site_data_dd_href

    json_dd = get_sub_menus(
        f'{data_format.upper()} DATA',
        data_href,
        data_menu_dict,
        sub_menu_dd=''
    )

    return json_dd

def get_folders(rootdir):
    dir_dict = {}
    rootdir = rootdir.rstrip(os.sep)
    start = rootdir.rfind(os.sep) + 1
    for path, dirs, files in os.walk(rootdir):
        folders = path[start:].split(os.sep)
        subdir = dict.fromkeys(files)
        parent = reduce(dict.get, folders[:-1], dir_dict)
        parent[folders[-1]] = subdir
    return dir_dict

def get_site_name(site_id, meta):
    df = meta[meta['site_id'] == site_id]
    if not df.empty:
        return df['site_metadata.site_name'].iloc[0]
    return str(site_id)

def get_datatype_name(datatype_id, meta):
    df = meta[meta['datatype_id'] == datatype_id]
    if not df.empty:
        return df['datatype_metadata.datatype_common_name'].iloc[0]
    return datatype_id

def get_button(button_label, dropdown_str):
    nl = '\n'
    drop_down_str = (
        f'    <div class="dropdown">{nl}'
        f'        <button class="btn btn-outline-primary btn-lg '
        f'dropdown-toggle mt-3" type="button" '
        f'data-toggle="dropdown" aria-pressed="false" '
        f'autocomplete="on">{button_label}'
        f'<span class="caret"></span></button>{nl}'
        f'        <ul class="dropdown-menu">{nl}'
        f'            {dropdown_str}{nl}'
        f'        </ul>{nl}'
        f'    </div>{nl}'
    )

    return drop_down_str

def get_menu_entry(label, href):
    nl = '\n'
    return (
        f'<li><a tabindex="0" href="{href}">'
        f'<b><i>{label}</b></i></a></li>{nl}'
    )

def get_sub_menus(label, href, sub_menu_dict={}, sub_menu_dd=''):
    nl = '\n'
    dd_items = []
    for sub_label, sub_href in sorted(sub_menu_dict.items()):
        dd_items.append(
            f'<li><a tabindex="0" href="{sub_href}">{sub_label}</a></li>{nl}'
        )

    sub_menu_str = ''
    if sub_menu_dd:
        sub_menu_str = f'{sub_menu_dd}{nl}'

    sub_menu_str = (
        f'<li class="dropdown-submenu">{nl}'
        f'<a class="test" tabindex="0" href="{href}">'
        f'{label}<span class="caret"></span></a>{nl}'
        f'    <ul class="dropdown-menu">{nl}'
        f'        {"".join(dd_items)}{nl}'
        f'            {sub_menu_str}'
        f'    </ul>{nl}'
        f'</li>{nl}'
    )

    return sub_menu_str

def get_site_submenu_str(data_dir, site_data, site_id, button_label, meta):
    charts_dd = []
    json_dd = []
    csv_dd = []
    for datatype, charts in site_data.items():
        if 'charts' in datatype:
            charts_dd = create_chart_dd(
                button_label,
                site_id,
                charts,
                data_dir
            )

        if 'json' in datatype:
            json_dd = create_data_dd(
                button_label,
                site_id,
                charts,
                data_dir,
                meta,
                'json'
            )

        if 'csv' in datatype:
            csv_dd = create_data_dd(
                button_label,
                site_id,
                charts,
                data_dir,
                meta,
                'csv'
            )

    site_submenu_str = '\n'.join(
        [i for i in [csv_dd, json_dd, charts_dd] if i]
    )

    return site_submenu_str

def create_nav(data_dir, nav_filename=None):
    nl = '\n'
    if not nav_filename:
        nav_filename = 'ff_nav.html'

    basepath = os.path.basename(os.path.normpath(data_dir))
    walk_dict = get_folders(data_dir)[basepath]
    to_remove = ['.git', 'pau_www.usbr.gov_uc_water_ff.csv']
    walk_dict = remove_items(to_remove, walk_dict)
    button_str_list = []
    for button_label, dd_items in walk_dict.items():
        if dd_items:
            to_remove = ['huc_maps']
            dd_items = remove_items(to_remove, dd_items)
            button_path_abs = Path(data_dir, button_label)
            meta_path = Path(button_path_abs, 'meta.csv')
            meta = pd.read_csv(meta_path)
            button_path = Path('.', button_label)
            meta_path = Path(button_path, 'meta.csv')
            map_path = Path(button_path, 'site_map.html')
            meta_menu_entry = get_menu_entry('METADATA', meta_path)
            map_menu_entry = get_menu_entry('SITE MAP', map_path)
            site_menu_list = [meta_menu_entry, map_menu_entry]
            site_name_dict = {
                get_site_name(int(k), meta): k for k, v in dd_items.items() if v
            }

            for site_name, site_id in sorted(site_name_dict.items()):
                site_path = Path(button_path, site_id)
                site_path_abs = Path(button_path_abs, site_id)
                dash_html_str = create_dash(site_name, site_id, site_path_abs)
                dash_filename = 'dashboard.html'
                dash_path_abs = Path(site_path_abs, dash_filename)
                dash_path = Path(site_path, dash_filename)
                dash_write_dict = {
                    dash_path_abs: dash_html_str
                }
                write_file(dash_write_dict)
                dash_menu_entry = get_menu_entry('DASHBOARD', dash_path)
                site_label = f'&bull; {site_name}'
                site_submenu_list = [dash_menu_entry]
                site_submenu_list.append(
                    get_site_submenu_str(
                        '.',
                        dd_items[site_id],
                        site_id,
                        button_label,
                        meta
                    )
                )
                site_submenu_str = '\n'.join(site_submenu_list)
                site_dd = get_sub_menus(
                    site_label,
                    site_path,
                    sub_menu_dd=site_submenu_str
                )
                site_menu_list.append(site_dd)
            sites_dd_str = '\n'.join(site_menu_list)
            folder_button = get_button(
                button_label.replace('_', ' '),
                sites_dd_str
            )
            button_str_list.append(folder_button)

    buttons_str = '\n'.join([i for i in button_str_list if i])

    nl = '\n'
    nav_html_str = (
        f'{HEADER_STR}{nl}{get_updt_str()}{nl}{buttons_str}{nl}{FOOTER_STR}'
    )
    write_nav_dict = {
        Path(data_dir, nav_filename): nav_html_str
    }
    write_file(write_nav_dict)

    return f'\nNavigation files created.'

if __name__ == '__main__':
    this_dir = os.path.dirname(os.path.realpath(__file__))
    data_dir = os.path.join(this_dir, 'flat_files')
#    data_dir = r'C:\Users\buriona\Documents\flat_files'
    sys_out = create_nav(data_dir)
    print(sys_out)
