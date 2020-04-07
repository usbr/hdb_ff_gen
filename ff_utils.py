# -*- coding: utf-8 -*-
"""
Created on Fri Sep 13 15:26:04 2019

@author: buriona
"""

import re
import json
from os import path
from datetime import datetime
import folium
import branca
import pandas as pd
from requests import get as r_get
from shapely.geometry import Point

STATIC_URL = f'https://www.usbr.gov/uc/water/hydrodata/assets'
NRCS_CHARTS_URL = 'https://www.nrcs.usda.gov/Internet/WCIS/basinCharts/POR'

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
            0: 'reservoir',
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
            0: 'tint',
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

def add_huc_layer(huc_map, level='2', json_path=None, embed=False, show=False,
                  use_topo=False):
   
    try:
        weight = -0.25 * float(level) + 2.5
        huc_style = lambda x: {
            'fillColor': '#ffffff00', 'color': '#A9A9A9AA', 'weight': weight
        }
        if use_topo:
            if not json_path:
                json_path = f'{STATIC_URL}/gis/HUC{level}.topojson'
            object_path = f'objects.HUC{level}'
            huc_topo_json = r_get(json_path).json()
            folium.TopoJson(
                huc_topo_json,
                object_path,
                name=f'HUC {level}',
                overlay=True,
                smooth_factor=2.0,
                style_function=huc_style,
                show=show
            ).add_to(huc_map)
        else:
            if not json_path:
                json_path = f'{STATIC_URL}/gis/HUC{level}.geojson'
            folium.GeoJson(
                json_path,
                name=f'HUC {level}',
                embed=embed,
                overlay=True,
                smooth_factor=2.0,
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

def get_huc_nrcs_stats(huc_level='6', try_all=False, add_export_dir=None):
    
    print(f'  Getting NRCS stats for HUC{huc_level}...')
    data_types = ['prec', 'wteq']
    index_pg_urls = [f'{NRCS_CHARTS_URL}/{i.upper()}/assocHUC{huc_level}' 
                     for i in data_types]
    index_pg_resps = [r_get(i) for i in index_pg_urls]
    index_pg_codes = [i.status_code for i in index_pg_resps]
    if not set(index_pg_codes) == set([200]):
        print(
            index_pg_urls, 
            f'  Could not download index file, trying all basins...'
        )
        try_all = True
        index_page_strs = ['' for i in index_pg_resps]
    else:
        index_page_strs = [i.text for i in index_pg_resps]
    topo_json_path = f'./gis/HUC{huc_level}.topojson'
    with open(topo_json_path, 'r') as tj:
        topo_json = json.load(tj)
    huc_str = f'HUC{huc_level}'
    swe_stat_dict = {}
    prec_stat_dict = {}
    topo_attrs = topo_json['objects'][huc_str]['geometries']
    for attr in topo_attrs:
        props = attr['properties']
        huc_name = props['Name']
        file_name = f'href="{huc_name.replace(" ", "%20")}.html"'
        if try_all or file_name in index_page_strs[0]:
            print(f'  Getting NRCS PREC stats for {huc_name}...')
            prec_stat = get_nrcs_basin_stat(
                huc_name, huc_level=huc_level, data_type='prec'
            )
            props['prec_percent'] = prec_stat
            prec_stat_dict[huc_name] = prec_stat
        else:
            props['prec_percent'] = "N/A"
            prec_stat_dict[huc_name] = "N/A"
        if try_all or file_name in index_page_strs[1]:
            print(f'  Getting NRCS WTEQ stats for {huc_name}...')
            swe_stat = get_nrcs_basin_stat(
                huc_name, huc_level=huc_level, data_type='wteq'
            )
            props['swe_percent'] = swe_stat
            swe_stat_dict[huc_name] = swe_stat
        else:
            props['swe_percent'] = "N/A"
            swe_stat_dict[huc_name] = "N/A"
    topo_json['objects'][huc_str]['geometries'] = topo_attrs
    
    geo_json_path = f'./gis/HUC{huc_level}.geojson'
    with open(geo_json_path, 'r') as gj:
        geo_json = json.load(gj)
    geo_features = geo_json['features']
    for geo_feature in geo_features:
        geo_props = geo_feature['properties']
        huc_name = geo_props['Name']
        geo_props['prec_percent'] = prec_stat_dict.get(huc_name, 'N/A')
        geo_props['swe_percent'] = swe_stat_dict.get(huc_name, 'N/A')
    
    geo_json['features'] = geo_features
    geo_export_paths = [geo_json_path]
    topo_export_paths = [topo_json_path]
    if add_export_dir:
        if path.isdir(add_export_dir):
            print(f'Exporting to alt dir: {add_export_dir}')
            add_geo_path = path.join(
                add_export_dir, 
                f'HUC{huc_level}.geojson'
            )
            geo_export_paths.append(add_geo_path)
            add_topo_path = path.join(
                add_export_dir, 
                f'HUC{huc_level}.topojson'
            )
            topo_export_paths.append(add_topo_path)
        else:
            print(f'Cannot export to alt dir: {add_export_dir}, does not exist')
    for export_path in geo_export_paths:
        with open(export_path, 'w') as tj:
            json.dump(geo_json, tj)
    for export_path in topo_export_paths:
        with open(export_path, 'w') as tj:
            json.dump(topo_json, tj)
    
def get_nrcs_basin_stat(basin_name, huc_level='2', data_type='wteq'):
    
    stat_type_dict = {'wteq': 'Median', 'prec': 'Average'}
    url = f'{NRCS_CHARTS_URL}/{data_type.upper()}/assocHUC{huc_level}/{basin_name}.html'
    try:
        response = r_get(url)
        if not response.status_code == 200:
            print(f'      Skipping {basin_name} {data_type.upper()}, NRCS does not publish stats.')
            return 'N/A'
        html_txt = response.text
        stat_type = stat_type_dict.get(data_type, 'Median')
        regex = f"(?<=% of {stat_type} - )(.*)(?=%<br>%)"
        swe_re = re.search(regex, html_txt, re.MULTILINE)
        stat = html_txt[swe_re.start():swe_re.end()]
    except Exception as err:
        print(f'      Error gathering data for {basin_name} - {err}')
        stat = 'N/A'
    return stat

def add_huc_chropleth(m, data_type='swe', show=False, huc_level='6', 
                      gis_path='gis', filter_str=None, use_topo=False):
    
    huc_str = f'HUC{huc_level}'
    stat_type_dict = {'swe': 'Median', 'prec': 'Avg.'}
    stat_type = stat_type_dict.get(data_type, '')
    layer_name = f'{huc_str} % {stat_type} {data_type.upper()}'
    if use_topo:
        topo_json_path = path.join(gis_path, f'{huc_str}.topojson')
        with open(topo_json_path, 'r') as tj:
            topo_json = json.load(tj)
        if filter_str:
            topo_json = filter_topo_json(
                topo_json, huc_level=huc_level, filter_str=filter_str
            )
    style_function = lambda x: style_chropleth(
        x, data_type=data_type, huc_level=huc_level, huc_filter=filter_str
    )
       
    if use_topo:
        folium.TopoJson(
            topo_json,
            f'objects.{huc_str}',
            name=layer_name,
            overlay=True,
            show=show,
            smooth_factor=2.0,
            style_function=style_function,
            tooltip=folium.features.GeoJsonTooltip(
                ['Name', f'{data_type}_percent'],
                aliases=['Basin Name:', f'{layer_name}:'])
        ).add_to(m)
    else:
        json_path = f'{STATIC_URL}/gis/HUC{huc_level}.geojson'
        folium.GeoJson(
            json_path,
            name=layer_name,
            embed=False,
            overlay=True,
            control=True,
            smooth_factor=2.0,
            style_function=style_function,
            show=show,
            tooltip=folium.features.GeoJsonTooltip(
                ['Name', f'{data_type}_percent'],
                aliases=['Basin Name:', f'{layer_name}:'])
        ).add_to(m)

def style_chropleth(feature, data_type='swe', huc_level='2', huc_filter='14'):
    huc_filter = str(huc_filter)
    huc_level = str(huc_level)
    colormap = get_colormap()
    stat_value = feature['properties'].get(f'{data_type}_percent', 'N/A')
    huc_id = str(feature['properties'].get(f'HUC{huc_level}', 'N/A'))
    if not stat_value == 'N/A':
        stat_value = float(stat_value)
    return {
        'fillOpacity': 0 if stat_value == 'N/A' or huc_id[:len(huc_filter)] != huc_filter else 0.75,
        'weight': 0,
        'fillColor': '#00000000' if stat_value == 'N/A' or huc_id[:len(huc_filter)] != huc_filter else colormap(stat_value)
    }

def filter_geo_json(geo_json_path, filter_attr='HUC2', filter_str='14'):
   
    f_geo_json = {'type': 'FeatureCollection'}
    with open(geo_json_path, 'r') as gj:
        geo_json = json.load(gj)
    features = [i for i in geo_json['features'] if 
                i['properties'][filter_attr][:2] == filter_str]
    f_geo_json['features'] = features
    
    return f_geo_json

def filter_topo_json(topo_json, huc_level=2, filter_str='14'):
    
    geometries = topo_json['objects'][f'HUC{huc_level}']['geometries']
    geometries[:] = [i for i in geometries if 
                i['properties'][f'HUC{huc_level}'][:len(filter_str)] == filter_str]
    topo_json['geometries'] = geometries
    return topo_json

def get_colormap(low=50, high=150):

    colormap = branca.colormap.LinearColormap(
        colors=[
            (255,51,51,150), 
            (255,255,51,150), 
            (51,255,51,150), 
            (51,153,255,150), 
            (153,51,255,150)
        ], 
        index=[50, 75, 100, 125, 150], 
        vmin=50,
        vmax=150
    )
    colormap.caption = '% of Average Precipitation or % Median Snow Water Equivalent'
    return colormap

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

if __name__ == '__main__':
    print('Just a utility module')
