# -*- coding: utf-8 -*-
"""
Created on Fri May 31 07:43:40 2019

@author: buriona
"""

from os import path
import folium
from folium.plugins import FloatImage, MousePosition
import pandas as pd
from ff_utils import get_fa_icon
from ff_utils import add_optional_tilesets, add_huc_layer, clean_coords
from ff_utils import get_bor_seal, get_favicon, get_icon_color
from ff_utils import get_bor_js, get_bor_css
from ff_utils import get_default_js, get_default_css

pd.options.mode.chained_assignment = None

bor_js = get_bor_js()
bor_css = get_bor_css()

default_js = get_default_js()
default_css = get_default_css()

#folium.folium._default_js = default_js
#folium.folium._default_css = default_css
#folium.folium._default_js = bor_js
#folium.folium._default_css = bor_css

def get_bounds(meta):
    meta.drop_duplicates(subset='site_id', inplace=True)
    lats = []
    longs = []
    for index, row in meta.iterrows():
        try:
            lat = float(row['site_metadata.lat'])
            lon = float(row['site_metadata.longi'])
            if 0 <= lat <= 180:
                lats.append(lat)
            if -180 <= lon <= 0:
                longs.append(lon)
        except (ValueError, TypeError):
            pass

    max_lat = max(lats)
    max_long = -1 * max([abs(i) for i in longs])
    min_lat = min(lats)
    min_long = -1 * min([abs(i) for i in longs])
    return [(min_lat, max_long), (max_lat, min_long)]

def add_markers(sitetype_map, meta):
    meta.drop_duplicates(subset='site_id', inplace=True)

    for index, row in meta.iterrows():
        try:
            site_id = row['site_id']
            obj_type = int(row['site_metadata.objecttype_id'])
            lat = float(row['site_metadata.lat'])
            lon = float(row['site_metadata.longi'])
            elev = row.get('site_metadata.elevation', 'N/A')
            lat_long = [lat, lon]
            site_name = row['site_metadata.site_name']
            href = f'./{site_id}/dashboard.html'
            embed = f'''<div class="container embed-responsive embed-responsive-16by9">
                  <embed class="embed-responsive-item" src="{href}"></embed>
                </div>'''

            icon = get_fa_icon(obj_type)
            color = get_icon_color(row)
            popup_html = (
                f'{embed}'
                f'Latitude: {round(lat, 3)}, '
                f'Longitude: {round(lon, 3)}, '
                f'Elevation: {elev} <br>'
            )
            popup = folium.map.Popup(
                html=popup_html,
                max_width='75%'
            )
            folium.Marker(
                location=lat_long,
                popup=popup,
                tooltip=site_name,
                icon=folium.Icon(icon=icon, prefix='fa', color=color)
            ).add_to(sitetype_map)
        except (ValueError, TypeError) as err:
            if site_name:
                print(f'    Could not add {site_name} to site map - {err}')
            else:
                print(f'    Could not add {site_id} to site map, missing site_name')
            pass

def create_map(site_type, meta, data_dir):
    meta = meta.drop_duplicates(subset='site_id')
    meta['site_metadata.lat'] = clean_coords(meta['site_metadata.lat'])
    meta['site_metadata.longi'] = clean_coords(meta['site_metadata.longi'], True)
    sitetype_dir = path.join(data_dir, site_type)
    map_filename = f'site_map.html'
    map_path = path.join(sitetype_dir, map_filename)

    sitetype_map = folium.Map(
        tiles='Stamen Terrain'
    )
    bounds = get_bounds(meta.copy())
    if bounds:
        sitetype_map.fit_bounds(bounds)
        add_markers(sitetype_map, meta.copy())
        add_huc_layer(sitetype_map, 2)
        add_huc_layer(sitetype_map, 6)
        add_optional_tilesets(sitetype_map)
        folium.LayerControl().add_to(sitetype_map)
        FloatImage(
            get_bor_seal(orient='shield'),
            bottom=1,
            left=1
        ).add_to(sitetype_map)
        MousePosition(prefix="Location: ").add_to(sitetype_map)
        sitetype_map.save(map_path)
        flavicon = (
            f'<link rel="shortcut icon" '
            f'href="{get_favicon()}"></head>'
        )
        with open(map_path, 'r') as html_file:
            chart_file_str = html_file.read()

        with open(map_path, 'w') as html_file:
            chart_file_str = chart_file_str.replace(r'</head>', flavicon)
            replace_str = (
                '''left:1%;
                        max-width:10%;
                        max-height:10%;'''
            )
            chart_file_str = chart_file_str.replace(r'left:1%;', replace_str)
            html_file.write(chart_file_str)

        return f'Created site map for {site_type}'
    else:
        return 'Failed to create map for {site_type}, no sites with coordinates'

if __name__ == '__main__':
    this_dir = path.dirname(path.realpath(__file__))
    data_dir = path.join(this_dir, 'flat_files')

    site_types = ['GAUGE_DATA', 'RESERVOIR_DATA']
    for site_type in site_types:
        site_type_dir = path.join(data_dir, site_type)
        meta_path = path.join(data_dir, site_type, 'meta.csv')
        meta = pd.read_csv(meta_path)

        create_map(site_type, meta, data_dir)
