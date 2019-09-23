# -*- coding: utf-8 -*-
"""
Created on Fri Feb 15 13:54:32 2019

@author: buriona
"""

import time
import json
import sys
import logging
import pandas as pd
import numpy as np
import plotly as py
from datetime import datetime as dt
from os import path, makedirs
from ff_nav import create_nav
from ff_site_maps import create_map
from ff_charts import create_chart
from ff_scp_push import push_scp
from ff_webmap_gen import create_webmap
from ff_huc_maps import create_huc_maps
from ff_to_rise import ff_to_rise
from hdb_api.hdb_utils import get_eng_config
from hdb_api.hdb_api import Hdb, HdbTables, HdbTimeSeries
from logging.handlers import TimedRotatingFileHandler

def get_plot_config(img_filename):
    return {
        'modeBarButtonsToRemove': [
            'sendDataToCloud',
            'lasso2d',
            'select2d'
        ],
        'showAxisDragHandles': True,
        'showAxisRangeEntryBoxes': True,
        'displaylogo': False,
        'toImageButtonOptions': {
            'filename': img_filename,
            'width': 1200,
            'height': 700
        }
    }

def create_log(path='ff_gen.log'):
    logger = logging.getLogger('ff_gen rotating log')
    logger.setLevel(logging.INFO)

    handler = TimedRotatingFileHandler(
        path,
        when="W6",
        backupCount=1
    )

    logger.addHandler(handler)

    return logger

def sync_files(this_dir, script_name, logger):
    try:
        print(f'Attempting sftp push using {script_name}...')
        scp_push_str = push_scp(this_dir, script_name)
        print(scp_push_str)
        logger.info(scp_push_str)
    except Exception as err:
        sftp_push_err = (
            f'Error running file sync script - {err}'
        )
        print(sftp_push_err)
        logger.info(sftp_push_err)

def make_chart(df, meta, chart_filename, img_filename, logger, plotly_js=None):
    if not plotly_js:
        plotly_js = (
            r'https://www.usbr.gov/uc/water/ff/static/js/plotly/1.47.4/plotly.min.js'
        )
    try:
        fig = create_chart(df.copy(), meta)
        py.offline.plot(
            fig,
            include_plotlyjs=plotly_js,
            config=get_plot_config(img_filename),
            filename=chart_filename,
            auto_open=False
        )

        flavicon = (
            f'<link rel="shortcut icon" '
            f'href="https://www.usbr.gov/img/favicon.ico"></head>'
        )
        with open(chart_filename, 'r') as html_file:
            chart_file_str = html_file.read()

        with open(chart_filename, 'w') as html_file:
            html_file.write(chart_file_str.replace(r'</head>', flavicon))

    except Exception as err:
        err_str = (
            f'     Error creating chart - '
            f'{chart_filename.split("flat_files")[-1]} - {err}'
        )
        print(err_str)
        logger.info(err_str)

def make_csv(df, csv_filename, logger):
    try:
        df.to_csv(csv_filename, index=False)
    except Exception as err:
        csv_err = f'Error saving {csv_filename} - {err}'
        print(csv_err)
        logger.info(csv_err)

def make_json(df, json_filename, logger):
    try:
        df['datetime'] = df['datetime'].dt.strftime('%Y-%m-%d')
        df.to_json(json_filename, orient='split', index=False)
    except Exception as err:
        json_err = f'Error saving {json_filename} - {err}'
        print(json_err)
        logger.info(json_err)

def make_rise(df, db_name, site_name, datatype_name, interval,
              num_records, rise_dir, logger):
    try:
        df['datetime'] = df['datetime'].dt.strftime('%Y-%m-%d')
        ff_to_rise(
            df,
            db_name,
            site_name,
            datatype_name,
            interval,
            num_records,
            rise_dir
        )
    except Exception as err:
        rise_err = (
            f'Error saving RISE.json for {site_name} {datatype_name} - {err}'
        )
        print(rise_err)
        logger.info(rise_err)

def make_nav(data_dir, logger):
    try:
        nav_str = create_nav(data_dir)
        print(nav_str)
        logger.info(nav_str)
    except Exception as err:
        nav_str = (
            f'Error creating ff_nav.html file for {data_dir} - {err}'
        )
        print(nav_str)
        logger.info(nav_str)

def make_sitemap(site_type, df_meta, data_dir, logger):
    try:
        map_str = create_map(site_type, df_meta, data_dir)
        print(map_str)
        logger.info(map_str)
    except Exception as err:
        map_str = (
            f'Error creating leaflet map file for {site_type} - {err}'
        )
        print(map_str)
        logger.info(map_str)

def make_webmap(data_dir, logger):
    try:
        webmap_str = create_webmap(data_dir)
        print(webmap_str)
        logger.info(webmap_str)
    except Exception as err:
        webmap_err = (
            f'Error creating webmap - {err}'
        )
        print(webmap_err)
        logger.info(webmap_err)

def make_huc_maps(df_meta, site_type_dir):
    try:
        huc_map_str = create_huc_maps(df_meta, site_type_dir)
        print(huc_map_str)
        logger.info(huc_map_str)
    except Exception as err:
        webmap_err = (
            f'Error creating huc maps - {err}'
        )
        print(webmap_err)
        logger.info(webmap_err)

if __name__ == '__main__':

    this_dir = path.dirname(path.realpath(__file__))

    schema = sys.argv[-1]
    if schema == sys.argv[0]:
        schema = 'default'

    with open('ff_config.json', 'r') as fp:
        ff_config = json.load(fp)[schema]

    data_dir = ff_config['alt_path']
    if not data_dir:
        data_dir = path.join(this_dir, 'flat_files')

    makedirs(data_dir, exist_ok=True)
    rise_dir = path.join(this_dir, 'rise')
    makedirs(rise_dir, exist_ok=True)

    logger = create_log(path.join(data_dir, 'ff_gen.log'))
    hdb_config = get_eng_config(db=ff_config['hdb'])
    db_name = hdb_config['database']
    hdb = Hdb(hdb_config)
    tbls = HdbTables
    ts = HdbTimeSeries

    schema_str = (
        f'\nUsing "{schema}" schema...\n\n'
        f'  Pushing files to: {data_dir.replace(this_dir, "..")} '
        f' @ {dt.now().strftime("%x %X")} '
    )
    print(schema_str)
    logger.info(schema_str)

    for site_type, type_config in ff_config['requests'].items():
        folder_str = (f'\n  Populating "{site_type}" folder...\n')
        print(folder_str)
        logger.info(folder_str)

        site_type_dir = path.join(data_dir, site_type)
        makedirs(site_type_dir, exist_ok=True)

        interval = type_config['interval']
        if interval not in ['instant', 'hour', 'day', 'month', 'year']:
            interval = 'day'
        period = type_config['period'].upper()
        sids = type_config['sids']
        dids = type_config['dids']

        df_meta = tbls.sitedatatypes(
            hdb,
            sid_list=sids,
            did_list=dids
        )

        df_meta['last_meas_date'] = pd.NaT
        df_meta['last_meas_val'] = np.NaN

        sdis = df_meta.index.tolist()
        datatype_label = 'datatype_metadata.datatype_common_name'
        datatype_names = df_meta[datatype_label].tolist()
        datatype_ids = df_meta['datatype_id'].tolist()
        site_ids = df_meta['site_id'].tolist()

        site_label = 'site_metadata.site_name'
        site_names = df_meta[site_label].tolist()
        metadata_filename = path.join(site_type_dir, 'meta.csv')
        df_meta.to_csv(metadata_filename, index=False)

        for i, sdi in enumerate(sdis):
            bt = time.time()

            created_site_str = (
                f'    Creating flat files for '
                f'{site_names[i]} - {datatype_names[i]}...'
            )
            print(created_site_str)
            logger.info(created_site_str)

            meta = df_meta[df_meta.index == [sdi]].iloc[0]

            site_dir = path.join(site_type_dir, f'{site_ids[i]}')
            csv_dir = path.join(site_dir, 'csv')
            json_dir = path.join(site_dir, 'json')

            chart_dir = path.join(site_dir, 'charts')

            makedirs(site_dir, exist_ok=True)
            makedirs(csv_dir, exist_ok=True)
            makedirs(json_dir, exist_ok=True)
            makedirs(chart_dir, exist_ok=True)

            csv_filename = path.join(csv_dir, f'{datatype_ids[i]}.csv')
            chart_filename = path.join(chart_dir, f'{datatype_names[i]}.html')
            img_filename = f'{site_ids[i]}_{datatype_names[i]}'
            json_filename = path.join(json_dir, f'{datatype_ids[i]}.json')
            csv_filename = csv_filename.replace(' ', '_')
            chart_filename = chart_filename.replace(' ', '_')
            json_filename = json_filename.replace(' ', '_')

            df = ts.series(
                hdb,
                sdi=sdi,
                interval=interval,
                t1=period,
                t2=period
            )

            df.dropna(inplace=True)
            if not df.empty:
                idx = pd.date_range(df.index.min(), df.index.max())
                df = df.reindex(idx)
                df['datetime'] = df.index

#                make_rise(
#                    df.copy(),
#                    db_name,
#                    site_names[i],
#                    datatype_names[i],
#                    interval,
#                    14,
#                    rise_dir,
#                    logger
#                )
                make_chart(
                    df.copy(),
                    meta,
                    chart_filename,
                    img_filename,
                    logger
                )
                make_csv(df.copy(), csv_filename, logger)
                make_json(df.copy(), json_filename, logger)

                et = time.time()

                finsihed_str = (
                    f'     finished in {round(et - bt,2)} seconds.'
                )
                print(finsihed_str)
                logger.info(finsihed_str)

            else:
                no_data_str = (
                    f'     no data for {site_names[i]} - {datatype_names[i]}. '
                    f'No files were created.'
                )
                print(no_data_str)
                logger.info(no_data_str)

        metadata_filename = path.join(site_type_dir, 'meta.csv')
        df_meta.to_csv(metadata_filename, index=False)
        make_huc_maps(df_meta.copy(), site_type_dir)
        make_sitemap(site_type, df_meta, data_dir, logger)

    make_nav(data_dir, logger)

    make_webmap(data_dir, logger)

    logger.info(
        f'\nFinished ff_gen @ {dt.now().strftime("%x %X")}'
    )

    if ff_config['sftp_push']:
        pub_script_name = 'ff_scp_push.txt'
        sync_files(this_dir, pub_script_name, logger)
        rise_script_name = 'ff_rise_push.txt'
#        sync_files(this_dir, rise_script_name, logger)

    logger.info(('-- * ' * 25 + '\n')*2)

#    push_to_tdrive(from_dir, to_dir)
