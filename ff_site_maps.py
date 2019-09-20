# -*- coding: utf-8 -*-
"""
Created on Fri May 31 07:43:40 2019

@author: buriona
"""

from os import path
import folium
import pandas as pd
from ff_map_utils import get_bor_js, get_bor_css
from ff_map_utils import get_default_js, get_default_css

bor_js = get_bor_js()
bor_css = get_bor_css()

default_js = get_default_js()
default_css = get_default_css()

#folium.folium._default_js = default_js
#folium.folium._default_css = default_css
#folium.folium._default_js = bor_js
#folium.folium._default_css = bor_css

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
            lat = float(row['site_metadata.lat'])
            lon = float(row['site_metadata.longi'])
            elev = row['site_metadata.elevation']
            lat_long = [lat, lon]
            site_name = row['site_metadata.site_name']
            href = f'./{site_id}/dashboard.html'
            embed = f'''<div class="container embed-responsive embed-responsive-16by9">
                  <embed class="embed-responsive-item" src="{href}" scrolling="no" frameborder="0" allowfullscreen></embed>
                </div>'''

            popup_html = (
                f'<a href="{href}" target="_blank">OPEN IN NEW WINDOW</a><br>'
                f'{embed}'
                f'Latitude: {round(lat, 3)}, '
                f'Longitude: {round(lon, 3)}, '
                f'Elevation: {elev} <br>'
            )

            icon = 'tint'
            folium.Marker(
                location=lat_long,
                popup=popup_html,
                tooltip=site_name,
                icon=folium.Icon(icon=icon, prefix='fa')
            ).add_to(sitetype_map)
        except (ValueError, TypeError):
            pass

def create_map(site_type, meta, data_dir):
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
        sitetype_map.save(map_path)
        return f'Created map for {site_type}'
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
