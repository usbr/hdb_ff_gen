# -*- coding: utf-8 -*-
"""
Created on Fri Feb 15 13:54:32 2019

@author: buriona
"""

import time
import json
import sys
import logging
from os import path, makedirs, system
from datetime import datetime as dt
import pandas as pd
import numpy as np
import plotly as py
from logging.handlers import TimedRotatingFileHandler
from ff_nav import create_nav
from ff_site_maps import create_map
from ff_charts import create_chart
from ff_webmap_gen import create_webmap
from ff_huc_maps import create_huc_maps
from ff_to_rise import ff_to_rise
from ff_utils import get_favicon, get_plotly_js
from ff_utils import get_huc_nrcs_stats, get_plot_config
from hdb_api.hdb_utils import get_eng_config
from hdb_api.hdb_api import Hdb, HdbTables, HdbTimeSeries, HdbApiError

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

def sync_files(config_path, logger):
    from ff_sftp_push import push_sftp
    try:
        print(f'Attempting sftp push using {config_path}...')
        with open(config_path, 'r') as fp:
            sftp_configs = json.load(fp)
        for key, config_dict in sftp_configs.items():
            scp_push_str = push_sftp(
                config_dict=config_dict,
                del_local=True, 
                del_remote=True,
                file_type='*.json'
            )
            print(scp_push_str)
            logger.info(scp_push_str)
    except Exception as err:
        sftp_push_err = (
            f'  Error running file sync script - {err}'
        )
        print(sftp_push_err)
        logger.info(sftp_push_err)

def make_chart(df, meta, chart_filename, img_filename, logger, plotly_js=None):
    if not plotly_js:
        plotly_js = get_plotly_js()
    try:
        fig = create_chart(df.copy(), meta)
        py.offline.plot(
            fig,
            include_plotlyjs=plotly_js,
            config=get_plot_config(img_filename),
            filename=chart_filename,
            auto_open=False,
            validate=False,
        )

        flavicon = (
            f'<link rel="shortcut icon" '
            f'href="{get_favicon()}"></head>'
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
        csv_err = f'  Error saving {csv_filename} - {err}'
        print(csv_err)
        logger.info(csv_err)

def make_json(df, json_filename, logger):
    try:
        df['datetime'] = df['datetime'].dt.strftime('%Y-%m-%d')
        df.to_json(json_filename, orient='split', index=False)
    except Exception as err:
        json_err = f'  Error saving {json_filename} - {err}'
        print(json_err)
        logger.info(json_err)

def make_rise(df, db_name, site_id, site_name, datatype_id, datatype_name, 
              interval, num_records, rise_dir, logger):
    try:
        df['datetime'] = df['datetime'].dt.strftime('%Y-%m-%d')
        ff_to_rise(
            df,
            db_name,
            site_id,
            datatype_id,
            datatype_name,
            interval,
            num_records,
            rise_dir
        )
    except Exception as err:
        rise_err = (
            f'  Error saving RISE.json for {site_name} {datatype_name} - {err}'
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
            f'  Error creating ff_nav.html file for {data_dir} - {err}'
        )
        print(nav_str)
        logger.info(nav_str)

def make_sitemap(site_type, df_meta, data_dir, logger):
    try:
        print('Creating site map...')
        map_str = create_map(site_type, df_meta, data_dir)
        print(map_str)
        logger.info(map_str)
    except Exception as err:
        map_str = (
            f'  Error creating leaflet site map file for {site_type} - {err}'
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
            f'  Error creating webmap for {data_dir} - {err}'
        )
        print(webmap_err)
        logger.info(webmap_err)

def make_huc_maps(df_meta, site_type_dir, logger):
    try:
        huc_map_str = create_huc_maps(df_meta, site_type_dir)
        print(huc_map_str)
        logger.info(huc_map_str)
    except Exception as err:
        webmap_err = (
            f'  Error creating huc maps in {site_type_dir} - {err}'
        )
        print(webmap_err)
        logger.info(webmap_err)

def update_gis_files(huc_level, logger, add_export_dir=None):
    try:
        gis_str = (
            f'Updating HUC{huc_level} '
            f'GIS files with current NRCS data...'
        )
        print(gis_str)
        logger.info(gis_str)
        get_huc_nrcs_stats(huc_level=huc_level, add_export_dir=add_export_dir)
        gis_str = (
            f'  Successfully updated HUC{huc_level} '
            f'GIS files with current NRCS data.\n'
        )
        print(gis_str)
        logger.info(gis_str)
    except Exception as err:
        gis_str = (
            f'  Failed to update HUC{huc_level} '
            f'GIS files with current NRCS data - {err}\n'
        )
        print(gis_str)
        logger.info(gis_str)
        
def get_data(hdb, sdi, interval, json_filename, period='POR', logger=None):
    
    def try_api(hdb, sdi, interval, t1, t2, logger=None):
        for i in range(5):
            try:
                df_hdb = HdbTimeSeries.series(
                hdb, sdi=sdi, interval=interval, t1=t1, t2=t2
            )
            except HdbApiError as err:
                last_err = err
                err_str = (
                    f'     Error gathering ts data will retry {5- i} more times.\n'
                )
                print(err_str)
                if logger:
                    logger.info(err_str)
                for i in range(60):
                    time.sleep(0.5)
            else:
                return df_hdb
        
        err_str = (
            f'\nMax ts call retries exceeded, quitting ff_gen.\n{last_err}'
        )
        if logger:
            logger.info(err_str)
        sys.exit(err_str)
    
    if period.isnumeric() and path.exists(json_filename):
        df_local = pd.read_json(json_filename, orient='split')
        df_local.index = df_local['datetime']
        df_local.index.rename('datetime', inplace=True)
        e_date = dt.today()
        last_data_date = df_local.iloc[-1]['datetime']
        s_date = last_data_date - np.timedelta64(period, 'D')
        df_hdb = try_api(
            hdb=hdb, sdi=sdi, interval=interval, t1=s_date, t2=e_date
        )
        df = pd.concat(
            [df_hdb, df_local]
        ).drop_duplicates(subset='datetime', keep='first').sort_index()

    else:
        df = try_api(
            hdb=hdb, sdi=sdi, interval=interval, t1='POR', t2='POR'
        )
    df.dropna(inplace=True)
    return df

def get_metadata(hdb, sid_list=None, did_list=None, sdi_list=None, logger=None):
    for i in range(5):
        try:
            df_meta = HdbTables.sitedatatypes(
                hdb,
                sid_list=sid_list,
                did_list=did_list,
                sdi_list=sdi_list
            )
        except HdbApiError as err:
            last_err = err
            err_str = (
                f'  Error gathering metadata will retry {5 - i} more times -'
                f' {err}\n'
            )
            print(err_str)
            if logger:
                logger.info(err_str)
            for i in range(60):
                time.sleep(0.5)
        else:
            return df_meta
    
    err_str = (
        f'\nMax metadata call retries exceeded, quitting ff_gen.\n{last_err}'
    )
    if logger:
        logger.info(err_str)
    sys.exit(err_str)

def get_parent_metadata(hdb, ids=[], logger=None):
    for i in range(5):
        try:
            df_meta = HdbTables.sites(
                hdb,
                ids=ids
            )
        except HdbApiError as err:
            last_err = err
            err_str = (
                f'  Error gathering parent metadata will retry {5 - i} more times.\n'
            )
            print(err_str)
            if logger:
                logger.info(err_str)
            for i in range(60):
                time.sleep(0.5)
        else:
            return df_meta
    
    err_str = (
        f'\nMax metadata call retries exceeded, quitting ff_gen.\n{last_err}'
    )
    if logger:
        logger.info(err_str)
    sys.exit(err_str)

def swap_parent_meta(df_meta, parent_meta):
    huc_lbl = 'site_metadata.hydrologic_unit'
    elev_lbl = 'site_metadata.elevation'
    long_lbl = 'site_metadata.longi'
    lat_lbl = 'site_metadata.lat'
    name_lbl = 'site_metadata.site_name'
    parent_ids = [str(i) for i in parent_meta['site_id'].to_list()]
    for idx, row in df_meta.iterrows():
        parent_id = str(row['site_metadata.parent_site_id'])
        if parent_id in parent_ids:
            df_meta.loc[idx, 'site_id'] = parent_id
            df_meta.loc[idx, name_lbl] = parent_meta['site_name'].loc[parent_id]
            df_meta.loc[idx, lat_lbl] = parent_meta['lat'].loc[parent_id]
            df_meta.loc[idx, long_lbl] = parent_meta['longi'].loc[parent_id]
            df_meta.loc[idx, elev_lbl] = parent_meta['elevation'].loc[parent_id]
            df_meta.loc[idx, huc_lbl] = parent_meta['hydrologic_unit'].loc[parent_id]
    return df_meta

def accounting_meta(hdb, df_meta, logger=None):
    parent_site_ids = df_meta['site_metadata.parent_site_id']
    parent_site_ids = parent_site_ids.drop_duplicates().to_list()
    parent_site_ids[:] = [i for i in parent_site_ids if i]
    parent_meta = get_parent_metadata(
            hdb=hdb, ids=parent_site_ids, logger=logger
        )
    df_meta = swap_parent_meta(df_meta, parent_meta)
    return df_meta
    
if __name__ == '__main__':
    
    import argparse
    cli_desc = 'Creates HDB data portal flat files using schema defined in ff_config.json'
    parser = argparse.ArgumentParser(description=cli_desc)
    parser.add_argument("-V", "--version", help="show program version", action="store_true")
    parser.add_argument("-r", "--rise", help="create RISE jsons, push only if sftp_push set to true or valid path in config", action="store_true")
    parser.add_argument("-l", "--log", help="set logs to verbose or default to standard", choices=['verbose', 'standard'], default='standard')
    parser.add_argument("-o", "--output", help="override alt_path from config file output folder")
    parser.add_argument("-s", "--schema", help='schema to use, defaults to "default"')
    parser.add_argument("-c", "--config", help="use alternate config json, use full path")
    parser.add_argument("-m", "--maps", help="create huc-maps", action="store_true")
    parser.add_argument("-g", "--gis", help="update gis files with current NRCS data", action='store_true')
    parser.add_argument("-n", "--no_charts", help="create huc-maps", action="store_true")
    
    args = parser.parse_args()
    
    if args.version:
        print('ff_gen.py v1.0')
    
    create_rise = False
    if args.rise:
        create_rise = True

    this_dir = path.dirname(path.realpath(__file__))
    
    if args.config:
        config_path = args.config
        if not path.exists(config_path):
            print(f'{args.config} does not exist in config file, try again.')
            sys.exit(0)
    else:
        config_path = path.join(this_dir, 'ff_config.json')
        
    with open(config_path, 'r') as fp:
        ff_config_dict = json.load(fp)
    
    if args.schema:
        schema = args.schema
        if not schema in ff_config_dict:
            print(f'{schema} is not within the config file ({config_path}), try again.')
            sys.exit(0)
    else:
        schema = 'default'
        
    ff_config = ff_config_dict[schema]
    
    data_dir = ff_config['alt_path']
    if not data_dir:
        data_dir = path.join(this_dir, 'flat_files')
    if args.output:
        data_dir = args.output
        if not path.exists(data_dir):
            print(f'{data_dir} does not exist, can not save files there, try again.')
            sys.exit(0)
    
    rise_sites = ff_config['rise_sites']
    if not rise_sites:
        rise_sites = []
    rise_sites[:] = [str(i) for i in rise_sites]
    
    makedirs(data_dir, exist_ok=True)
    
    logger = create_log(path.join(data_dir, 'ff_gen.log'))
    hdb_config = get_eng_config(db=ff_config['hdb'])
    db_name = hdb_config['database']
    hdb = Hdb(hdb_config)
    ##################################################
    #remove replace statement once RISE gets it together **********
    rise_dir = path.join(this_dir, 'rise', db_name.replace('lchdb', 'lchdb2'))
    ######################################################
    makedirs(rise_dir, exist_ok=True)
    
    if args.gis:
        for huc_level in ['2', '6', '8']:
            assets_dir = path.join(data_dir, 'assets', 'gis')
            makedirs(assets_dir, exist_ok=True)
            update_gis_files(huc_level, logger, add_export_dir=assets_dir)

    s_time = dt.now()
    schema_str = (
        f'\nUsing "{schema}" schema...\n\n'
        f'  Pushing files to: {data_dir.replace(this_dir, "..")} '
        f' @ {s_time.strftime("%x %X")} '
    )
    print(schema_str)
    logger.info(schema_str)
    
    no_charts = False
    if args.no_charts:
        no_charts = args.no_charts
        no_chart_str = '    No charts flag provided, no charts/csv/json will be created.'
        print(no_chart_str)
        logger.info(no_chart_str)
        
    for site_type, type_config in ff_config['requests'].items():
        period = str(type_config['period']).upper()
        folder_str = (
            f'\n  Populating "{site_type}" folder, '
            f'using a refresh period of {period}...\n'
        )
        print(folder_str)
        logger.info(folder_str)

        site_type_dir = path.join(data_dir, site_type)
        makedirs(site_type_dir, exist_ok=True)

        interval = type_config['interval']
        if interval not in ['instant', 'hour', 'day', 'month', 'year']:
            interval = 'day'

        sids = type_config.get('sids', None)
        dids = type_config.get('dids', None)
        sdis = type_config.get('sdis', None)
        
        if sids or dids:
            df_meta = get_metadata(
                hdb=hdb, sid_list=sids, did_list=dids, logger=logger
            )
        else:
            df_meta = pd.DataFrame()
            
        if sdis:
            df_meta_sdi = get_metadata(
                hdb=hdb, sdi_list=sdis, logger=logger
            )
            df_meta = pd.concat([i for i in [df_meta, df_meta_sdi] if not i.empty])
            
        df_meta.drop_duplicates(
            inplace=True, 
            subset=['site_datatype_id', 'site_metadata.db_site_code'], 
            keep='last'
        )
        
        if type_config.get('mode', 'default') == 'accounting':
            df_meta = accounting_meta(hdb=hdb, df_meta=df_meta, logger=logger)

        df_meta['last_meas_date'] = pd.NaT
        df_meta['last_meas_val'] = np.NaN

        sdis = df_meta.index.tolist()
        datatype_label = 'datatype_metadata.datatype_common_name'
        datatype_names = df_meta[datatype_label].tolist()
        datatype_ids = df_meta['datatype_id'].tolist()
        site_ids = df_meta['site_id'].tolist()

        site_label = 'site_metadata.site_name'
        site_names = df_meta[site_label].tolist()
        site_common_label = 'site_metadata.site_common_name'
        site_common_names = df_meta[site_common_label].tolist()
        
        for i, sdi in enumerate(sdis):

            bt = time.time()

            meta = df_meta[df_meta.index == sdi].iloc[0]
            
            site_dir = path.join(site_type_dir, f'{site_ids[i]}')
            csv_dir = path.join(site_dir, 'csv')
            json_dir = path.join(site_dir, 'json')

            chart_dir = path.join(site_dir, 'charts')

            makedirs(site_dir, exist_ok=True)
            makedirs(csv_dir, exist_ok=True)
            makedirs(json_dir, exist_ok=True)
            makedirs(chart_dir, exist_ok=True)
            
            file_name_prefix = ''
            if type_config.get('mode', 'default') == 'accounting':
                file_name_prefix = f'{site_common_names[i].split("^")[-1]}_'
            csv_filename = path.join(csv_dir, f'{file_name_prefix}{datatype_ids[i]}.csv')
            chart_filename = path.join(chart_dir, f'{file_name_prefix}{datatype_names[i]}.html')
            img_filename = f'{file_name_prefix}{site_ids[i]}_{datatype_names[i]}'
            json_filename = path.join(json_dir, f'{file_name_prefix}{datatype_ids[i]}.json')
            csv_filename = csv_filename.replace(' ', '_')
            chart_filename = chart_filename.replace(' ', '_')
            json_filename = json_filename.replace(' ', '_')
            if no_charts:
                continue
            
            created_site_str = (
                f'    Creating hydroData files for '
                f'{site_names[i]} - {datatype_names[i]}'
            )
            print(created_site_str)
            if args.log == 'verbose':
                logger.info(created_site_str)

            df = get_data(
                hdb, sdi, interval, json_filename, period=period, logger=logger
            )

            if not df.empty:
                idx = pd.date_range(df.index.min(), df.index.max())
                df = df.reindex(idx)
                df['datetime'] = df.index
                
                if create_rise:
                    if str(site_ids[i]) in rise_sites:
                        num_records = str(period)
                        make_rise(
                            df.copy(),
                            db_name,
                            site_ids[i],
                            site_names[i],
                            datatype_ids[i],
                            datatype_names[i],
                            interval,
                            num_records,
                            rise_dir,
                            logger
                        )
                    
                make_chart(
                    df,
                    meta,
                    chart_filename,
                    img_filename,
                    logger
                )
                
                make_csv(df, csv_filename, logger)
                make_json(df, json_filename, logger)

                et = time.time()

                finished_str = (
                    f'     finished in {round(et - bt,2)} seconds.'
                )
                print(finished_str)
                if args.log == 'verbose':
                    logger.info(finished_str)

            else:
                no_data_str = (
                    f'     no data for {site_names[i]} - {datatype_names[i]}. '
                    f'No files were created.'
                )
                print(no_data_str)
                if args.log == 'verbose':
                    logger.info(no_data_str)
        
        if args.maps:
            make_huc_maps(df_meta.copy(), site_type_dir, logger)
                
        metadata_filename = path.join(site_type_dir, 'meta.csv')
        if path.isfile(metadata_filename):
            df_meta_old = pd.read_csv(metadata_filename)
            df_meta = pd.concat([df_meta_old, df_meta], ignore_index=True)
            df_meta.drop_duplicates(
                inplace=True, subset='site_datatype_id', keep='last'
            )
        df_meta.to_csv(metadata_filename, index=False)
        make_sitemap(site_type, df_meta.copy(), data_dir, logger)
        
    make_nav(data_dir, logger)

    # make_webmap(data_dir, logger)
    e_time = dt.now()
    d_time = e_time - s_time
    finish_str = (
        f'\nFinished ff_gen: {schema} @ {e_time.strftime("%x %X")} in '
        f"{':'.join(str(d_time).split(':')[:2])} hours"
    )
    print(finish_str)
    logger.info(finish_str)
    
    sftp_config = ff_config['sftp_push']
    if sftp_config and create_rise:
        if type(sftp_config) == bool:
            sync_files('sftp_config.json', logger)
        elif type(sftp_config) == str:
            if sftp_config.startswith(('rsync', 'sftp', 'scp', 'ftps')):
                sync_str = (
                    f'\nPushing data using the following command: {sftp_config}'
                )
                print(sync_str)
                logger.info(sync_str)
                system(sftp_config)
            elif path.exists(sftp_config):
                sync_files(sftp_config, logger)

    logger.info(('\n' + '-- * ' * 25)*2 + '\n')
