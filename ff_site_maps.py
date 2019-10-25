# -*- coding: utf-8 -*-
"""
Created on Fri May 31 07:43:40 2019

@author: buriona
"""

from os import path
import folium
from folium.plugins import FloatImage
import pandas as pd
from ff_utils import get_fa_icon
from ff_utils import get_bor_seal, get_favicon
from ff_utils import get_bor_js, get_bor_css
from ff_utils import get_default_js, get_default_css

bor_js = get_bor_js()
bor_css = get_bor_css()

default_js = get_default_js()
default_css = get_default_css()

#folium.folium._default_js = default_js
#folium.folium._default_css = default_css
#folium.folium._default_js = bor_js
#folium.folium._default_css = bor_css

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

def add_hu6_layer(huc_map, hu6_geojson_path=None, embed=False):
    if not hu6_geojson_path:
        hu6_geojson_path = 'https://gist.githubusercontent.com/beautah/01dd026c5b8fac1434959dfc48f775b5/raw/2e9e8a70ced3a1eca40cb0c2061fa689e9c44248/HUC6.geojson'
    huc6_style = lambda x: {
        'fillColor': '#ffffff00', 'color': '#1f1f1faa', 'weight': 2
    }

    folium.GeoJson(
        hu6_geojson_path,
        name='HUC 6',
        embed=embed,
        style_function = huc6_style,
        show=False
    ).add_to(huc_map)

def get_bounds(meta):
    meta_no_dups = meta.drop_duplicates(subset='site_id')
    lats = []
    longs = []
    for index, row in meta_no_dups.iterrows():
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
    meta_no_dups = meta.drop_duplicates(subset='site_id')
    for index, row in meta_no_dups.iterrows():
        try:
            site_id = row['site_id']
            obj_type = int(row['site_metadata.objecttype_id'])
            lat = float(row['site_metadata.lat'])
            lon = float(row['site_metadata.longi'])
            elev = row['site_metadata.elevation']
            lat_long = [lat, lon]
            site_name = row['site_metadata.site_name']
            href = f'./{site_id}/dashboard.html'
            embed = f'''<div class="container embed-responsive embed-responsive-16by9">
                  <embed class="embed-responsive-item" src="{href}" scrolling="no" frameborder="0" allowfullscreen></embed>
                </div>'''

            icon = get_fa_icon(obj_type)
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
                icon=folium.Icon(icon=icon, prefix='fa')
            ).add_to(sitetype_map)
        except (ValueError, TypeError):
            pass

def create_map(site_type, meta, data_dir):
    this_dir = path.dirname(path.realpath(__file__))
    sitetype_dir = path.join(data_dir, site_type)
    map_filename = f'site_map.html'
    map_path = path.join(sitetype_dir, map_filename)
    gis_path = path.join(this_dir, 'gis')
    huc6_path = path.join(gis_path, 'HUC6.geojson')

    sitetype_map = folium.Map(
        tiles='Stamen Terrain'
    )
    bounds = get_bounds(meta.copy())
    if bounds:
        sitetype_map.fit_bounds(bounds)
        add_markers(sitetype_map, meta.copy())
        add_hu6_layer(sitetype_map, huc6_path, True)
        add_optional_tilesets(sitetype_map)
        folium.LayerControl().add_to(sitetype_map)
        FloatImage(
            get_bor_seal(orient='shield'),
            bottom=1,
            left=1
        ).add_to(sitetype_map)
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
