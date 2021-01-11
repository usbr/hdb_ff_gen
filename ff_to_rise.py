# -*- coding: utf-8 -*-
"""
Created on Thu May 30 07:03:56 2019

@author: buriona
"""

from os import path, makedirs
from datetime import datetime as dt
import pandas as pd

def ff_to_rise(df, db_name, site_id, datatype_id, datatype_name,
               interval='day', num_records=None, export_dir=None):

    this_dir = path.dirname(path.realpath(__file__))
    if not export_dir:
        export_dir = path.join(this_dir, 'rise')
    curr_date_str = dt.now().strftime('%Y-%m-%d %H:%M:00')
    rise_timestamp_str = dt.now().strftime('%Y%m%d%H%M%S')
    rise_filename = f'{db_name}_{rise_timestamp_str}.json'
    if num_records.isnumeric():
        df = df.tail(int(num_records))
    df.rename(
        index=str,
        columns={
            'datetime': 'dateTime',
            datatype_name: 'result'
        },
        inplace=True
    )

    df['dateTime'] = pd.to_datetime(df['dateTime'])
    df['dateTime'] = df['dateTime'].dt.strftime('%Y-%m-%d %H:%M:%S-07:00')
    #remove replace statement once RISE gets it together
    df['sourceCode'] = db_name.replace('lchdb', 'lchdb2')
    df['locationSourceCode'] = site_id
    df['parameterSourceCode'] = datatype_id
    df['modelNameSourceCode'] = None
    df['modelRunSourceCode'] = None
    df['modelRunMemberSourceCode'] = None
    df['status'] = None
    df['lastUpdate'] = f'{curr_date_str}-07:00'
    resultAttributes = {
        'resultType': 'observed',
        'timeStep': interval
    }
    df['resultAttributes'] = [resultAttributes] * len(df)
    df['modelRunName'] = None
    df['modelRunDateTime'] = None
    df['modelRunDescription'] = None
    df['modelRunAttributes'] = None
    df['modelRunMemberDesc'] = None

    export_path = path.join(export_dir, rise_filename)
    df.to_json(export_path, orient='records')

if __name__ == '__main__':

    from datetime import date, timedelta
    from hdb_api.hdb_utils import get_eng_config
    from hdb_api.hdb_api import Hdb, HdbTimeSeries
    hdb_config = get_eng_config(db='uc')
    db_name = hdb_config['database']
    hdb = Hdb(hdb_config)
    ts = HdbTimeSeries
    datatype_name = 'release volume'
    interval = 'day'
    this_dir = path.dirname(path.realpath(__file__))
    rise_dir = path.join(this_dir, 'test', 'rise')
    makedirs(rise_dir, exist_ok=True)
    test_data_dir = path.join(this_dir, 'test', 'data')

    today = date.today()
    today_str = today.strftime('%Y-%m-%d')
    two_weeks_back = today - timedelta(days=14)
    two_weeks_back_str = two_weeks_back.strftime('%Y-%m-%d')
    for obj_type in ['res_meta', 'gauge_meta']:
        test_path = path.join(test_data_dir, f'{obj_type}.csv')
        df_meta = pd.read_csv(test_path)
        for idx, row in df_meta.iterrows():
            site_label = 'site_metadata.site_id'
            site_name = row[site_label]
            datatype_label = 'datatype_metadata.datatype_id'
            datatype_name = row[datatype_label]
            print(f'Creating RISE json for {site_name} - {datatype_name}')
            sdi = row['site_datatype_id']
            df = ts.series(
                hdb,
                sdi=sdi,
                interval=interval,
                t1=two_weeks_back_str,
                t2=today
            )
            ff_to_rise(
                df,
                db_name,
                site_name,
                datatype_name,
                interval,
                40,
                rise_dir
              )
            break