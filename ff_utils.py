# -*- coding: utf-8 -*-
"""
Created on Fri Sep 13 15:26:04 2019

@author: buriona
"""
import folium
import pandas as pd
# import geopandas as gpd
from shapely.geometry import Point

STATIC_URL = f'https://www.usbr.gov/uc/water/ff/static'

def get_plotly_js():
    return f'{STATIC_URL}/js/plotly/1.47.4/plotly.min.js'

def get_bootstrap():
    return {
        'css': f'{STATIC_URL}/css/bootstrap/4.3.1/bootstrap.min.css',
        'js': f'{STATIC_URL}/js/bootstrap/4.3.1/bootstrap.bundle.min.js',
        'jquery': f'{STATIC_URL}/js/jquery/3.4.0/jquery.min.js'
    }

def get_favicon():
    return f'{STATIC_URL}/img/favicon.ico'

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
    return [
        ('leaflet',
         'https://cdn.jsdelivr.net/npm/leaflet@1.5.1/dist/leaflet.js'),
        ('jquery',
         'https://code.jquery.com/jquery-1.12.4.min.js'),
        ('bootstrap',
         'https://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/js/bootstrap.min.js'),
        ('awesome_markers',
         'https://cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.js'),  # noqa
        ]

def get_default_css():
    return [
        ('leaflet_css',
         'https://cdn.jsdelivr.net/npm/leaflet@1.5.1/dist/leaflet.css'),
        ('bootstrap_css',
         'https://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap.min.css'),
        ('bootstrap_theme_css',
         'https://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap-theme.min.css'),  # noqa
        ('awesome_markers_font_css',
         f'{STATIC_URL}/css/font-awesome.min.css'),
         ('awesome_markers_font_css',
         'https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css'),  # noqa
        ('awesome_markers_css',
         'https://cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.css'),  # noqa
        ('awesome_rotate_css',
         'https://rawcdn.githack.com/python-visualization/folium/master/folium/templates/leaflet.awesome.rotate.css'),  # noqa
        ]

def get_fa_icon(obj_type='default'):
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
        15: 'info',
        20: 'exchange'
    }
    fa_icon = fa_dict.get(obj_type, 'map-pin')
    return fa_icon

def get_icon_color(row):
    obj_owner = 'BOR'
    if not row.empty:
        if row['site_metadata.scs_id']:
            obj_owner = 'NRCS'
        if row['site_metadata.usgs_id']:
            obj_owner = 'USGS'
    color_dict = {
        'BOR': 'blue',
        'NRCS': 'red',
        'USGS': 'green',
    }
    icon_color = color_dict.get(obj_owner, 'black')
    return icon_color

def add_optional_tilesets(folium_map):
    tilesets = [
        'OpenStreetMap',
        'Stamen Toner',
        'Stamen Watercolor',
        'CartoDB positron',
        'CartoDB dark_matter',
    ]
    for tileset in tilesets:
        folium.TileLayer(tileset).add_to(folium_map)

def add_huc_layer(huc_map, level=2, huc_geojson_path=None, embed=False):
    try:
        if not huc_geojson_path:
            huc_geojson_path = f'{STATIC_URL}/gis/HUC{level}.geojson'
        huc_style = lambda x: {
            'fillColor': '#ffffff00', 'color': '#1f1f1faa', 'weight': 2
        }

        folium.GeoJson(
            huc_geojson_path,
            name=f'HUC {level}',
            embed=embed,
            style_function=huc_style,
            show=False
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

if __name__ == '__main__':
    print('Just a utility module')
