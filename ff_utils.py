# -*- coding: utf-8 -*-
"""
Created on Fri Sep 13 15:26:04 2019

@author: buriona
"""

from os import path
import folium
import pandas as pd
# import geopandas as gpd
from shapely.geometry import Point
from datetime import datetime

STATIC_URL = f'https://www.usbr.gov/uc/water/ff/assets'

def get_plotly_js():
    return f'{STATIC_URL}/plotly.js'

def get_favicon():
    return f'{STATIC_URL}/img/favicon.ico'

def get_bootstrap():
    return {
        'css': f'{STATIC_URL}/bootstrap/css/bootstrap.min.css',
        'js': f'{STATIC_URL}/bootstrap/js/bootstrap.bundle.js',
        'jquery': f'{STATIC_URL}/jquery.js',
        'popper': f'{STATIC_URL}/popper.js',
        'fa': f'{STATIC_URL}/font-awesome/css/font-awesome.min.css',
    }

def get_bor_seal(orient='default', grey=False):
    color = 'cmyk'
    if grey:
        color = 'grey'
    seal_dict = {
        'default': f'BofR-horiz-{color}.png',
        'shield': f'BofR-shield-cmyk.png',
        'vert': f'BofR-vert-{color}.png',
        'horz': f'BofR-horiz-{color}.png'
        }
    return f'{STATIC_URL}/img/{seal_dict[orient]}'

def get_bor_js():
    return [
        ('leaflet',
          f'{STATIC_URL}/js/leaflet/leaflet.js'),
        ('jquery',
          f'{STATIC_URL}/js/jquery/3.4.0/jquery.min.js'),
        ('bootstrap',
          f'{STATIC_URL}/js/bootstrap/3.2.0/js/bootstrap.min.js'),
        ('awesome_markers',
          f'{STATIC_URL}/js/leaflet/leaflet.awesome-markers.js'),  # noqa
        ]

def get_bor_css():
    return [
        ('leaflet_css',
          f'{STATIC_URL}/css/leaflet/leaflet.css'),
        ('bootstrap_css',
          f'{STATIC_URL}/css/bootstrap/3.2.0/css/bootstrap.min.css'),
        ('bootstrap_theme_css',
          f'{STATIC_URL}/css/bootstrap/3.2.0/css/bootstrap-theme.min.css'),  # noqa
        ('awesome_markers_font_css',
          f'{STATIC_URL}/css/font-awesome.min.css'),  # noqa
        ('awesome_markers_css',
          f'{STATIC_URL}/css/leaflet/leaflet.awesome-markers.css'),  # noqa
        ('awesome_rotate_css',
          f'{STATIC_URL}/css/leaflet/leaflet.awesome.rotate.css'),  # noqa
        ]

def get_default_js():
    bootstrap_dict = get_bootstrap()
    return [
        ('leaflet', 
         f'{STATIC_URL}/leaflet/js/leaflet.js'),
        ('jquery', 
         bootstrap_dict['jquery']),
        ('bootstrap', 
         bootstrap_dict['js']),
        ('awesome_markers', 
         f'{STATIC_URL}/leaflet-awesome-markers/leaflet.awesome-markers.min.js'),
        ('popper', 
         bootstrap_dict['popper']),
    ]

def get_default_css():
    bootstrap_dict = get_bootstrap()
    return [
        ('leaflet_css', 
         f'{STATIC_URL}/leaflet/css/leaflet.css'),
        ('bootstrap_css', 
         bootstrap_dict['css']),
        ('awesome_markers_font_css', 
          bootstrap_dict['fa']),
        ('awesome_markers_css', 
        f'{STATIC_URL}/leaflet-awesome-markers/leaflet.awesome-markers.css'),
        ('awesome_rotate_css', 
         f'{STATIC_URL}/leaflet-awesome-markers/leaflet.awesome.rotate.css'),
    ]

def get_obj_type_name(obj_type='default'):
    obj_type_dict = {
            'default': 'map-pin',
            1: 'basin',
            2: 'climate site (rain)',
            3: 'confluence',
            4: 'diversion',
            5: 'hydro power plant',
            6: 'reach',
            7: 'reservoir',
            8: 'climate site (snow)',
            9: 'stream gage',
            10: 'hydro plant unit',
            11: 'canal',
            12: 'acoustic velocity meter',
            13: 'water quality site',
            14: 'riverware data object',
            300: 'bio eval. site',
            305: 'agg. diversion site',
            'SCAN': 'climate site (rain)',
            'PRCP': 'climate site (rain)',
            'BOR': 'reservoir',
            'SNTL': 'climate site (snow)',
            'SNOW': 'climate site (snow)',
            'SNTLT': 'climate site (snow)',
            'USGS': 'stream gage',
            'MSNT': 'climate site (snow)',
            'MPRC': 'climate site (rain)'
        }
    return obj_type_dict.get(obj_type, 'N/A')

def get_fa_icon(obj_type='default', source='hdb'):
    if source.lower() == 'hdb':
        fa_dict = {
            'default': 'map-pin',
            1: 'sitemap',
            2: 'umbrella',
            3: 'arrow-down',
            4: 'exchange',
            5: 'plug',
            6: 'arrows-v',
            7: 'tint',
            8: 'snowflake-o',
            9: 'tachometer',
            10: 'cogs',
            11: 'arrows-h',
            12: 'rss',
            13: 'flask',
            14: 'table',
            300: 'info',
            305: 'exchange'
        }
    if source.lower() == 'awdb':
        fa_dict = {
            'default': 'map-pin',
            'SCAN': 'umbrella',
            'PRCP': 'umbrella',
            'BOR': 'tint',
            'SNTL': 'snowflake-o',
            'SNOW': 'snowflake-o',
            'SNTLT': 'snowflake-o',
            'USGS': 'tachometer',
            'MSNT': 'snowflake-o',
            'MPRC': 'umbrella'
        }
    fa_icon = fa_dict.get(obj_type, 'map-pin')
    return fa_icon

def get_icon_color(row, source='hdb'):
    if source.lower() == 'hdb':
        obj_owner = 'BOR'
        if not row.empty:
            if row['site_metadata.scs_id']:
                obj_owner = 'NRCS'
            if row['site_metadata.usgs_id']:
                obj_owner = 'USGS'
    if source.lower() == 'awdb':
        obj_owner = row
    color_dict = {
        'BOR': 'blue',
        'NRCS': 'red',
        'USGS': 'green',
        'COOP': 'gray',
        'SNOW': 'darkred',
        'PRCP': 'lightred',
        'SNTL': 'red',
        'SNTLT': 'lightred',
        'SCAN': 'lightred',
        'MSNT': 'orange',
        'MPRC': 'beige',
        
    }
    icon_color = color_dict.get(obj_owner, 'black')
    return icon_color

def add_optional_tilesets(folium_map):
    tilesets = {
        "Terrain": 'Stamen Terrain',
        'Street Map': 'OpenStreetMap',
        'Toner': 'Stamen Toner',
        'Watercolor': 'Stamen Watercolor',
        'Positron': 'CartoDB positron',
        'Dark Matter': 'CartoDB dark_matter',
    }
    for name, tileset in tilesets.items():
        folium.TileLayer(tileset, name=name).add_to(folium_map)

def add_huc_layer(huc_map, level=2, huc_geojson_path=None, embed=False):
    try:
        if not huc_geojson_path:
            huc_geojson_path = f'{STATIC_URL}/gis/HUC{level}.geojson'
        huc_style = lambda x: {
            'fillColor': '#ffffff00', 'color': '#1f1f1faa', 'weight': 2
        }
        show = False
        if level == 2:
            show = True
        folium.GeoJson(
            huc_geojson_path,
            name=f'HUC {level}',
            embed=embed,
            style_function=huc_style,
            show=show
        ).add_to(huc_map)
    except Exception as err:
        print(f'Could not add HUC {level} layer to map! - {err}')

def clean_coords(coord_series, force_neg=False):
    
    coord_series = coord_series.apply(
        pd.to_numeric, 
        errors='ignore', 
        downcast='float'
    )
    if not coord_series.apply(type).eq(str).any():
        if force_neg:
            return -coord_series.abs()
        return coord_series
    results = []
    for idx, coord in coord_series.iteritems():
        if not str(coord).isnumeric():
            coord_strs = str(coord).split(' ')
            coord_digits = []
            for coord_str in coord_strs:
                coord_digit = ''.join([ch for ch in coord_str if ch.isdigit() or ch == '.'])
                coord_digits.append(float(coord_digit))
            dec = None
            coord_dec = 0
            for i in reversed(range(0, len(coord_digits))):
                if dec:
                    coord_dec = abs(coord_digits[i]) + dec
                dec = coord_digits[i] / 60
            if str(coord)[0] == '-':
                coord_dec = -1 * coord_dec
            results.append(coord_dec)
        else:
            results.append(coord)
    if force_neg:
        results[:] = [-1 * result if result > 0 else result for result  in results]
    clean_series = pd.Series(results, index=coord_series.index)
    return clean_series

def get_huc(geo_df, lat, lon, level='12'):

    for idx, row in geo_df.iterrows():
        polygon = row['geometry']
        point = Point(lon, lat)
        if polygon.contains(point):
            return row[f'HUC{level}']
    return None

def get_season():
    curr_month = datetime.now().month
    if curr_month > 3:
        return 'spring'
    if curr_month > 5:
        return 'summer'
    if curr_month > 10:
        return 'fall'
    return 'winter'

if __name__ == '__main__':
    print('Just a utility module')
