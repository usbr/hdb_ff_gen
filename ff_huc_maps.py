# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 08:14:46 2019

@author: buriona
"""

import json
from os import path, makedirs
from copy import deepcopy
from collections import OrderedDict
import folium
from folium.plugins import FloatImage, MousePosition
import pandas as pd
import numpy as np
#from requests import get as req_get
import geopandas as gpd
from shapely.geometry import Point
from shapely.ops import cascaded_union
from ff_utils import get_fa_icon, get_icon_color
from ff_utils import add_optional_tilesets, add_huc_layer, clean_coords, get_huc
from ff_utils import get_favicon, get_bor_seal
from ff_utils import get_bor_js, get_bor_css
from ff_utils import get_default_js, get_default_css

bor_js = get_bor_js()
bor_css = get_bor_css()

default_js = get_default_js()
default_css = get_default_css()

#folium.folium._default_js = default_js
folium.folium._default_css = default_css
#folium.folium._default_js = bor_js
#folium.folium._default_css = bor_css

def get_upstream_basin(huc12, to_huc_table):
    if huc12:
        huc12 = str(huc12)
        huc_list = [huc12]
        downstream_hucs = [huc12]
        to_huc_table = to_huc_table['objects'][f'{huc12[:2]}_HUC12']['geometries']
        for downstream_huc in downstream_hucs:
            upstream_hucs = get_upstream_hucs(downstream_huc, to_huc_table)
            downstream_hucs.extend(upstream_hucs)
            huc_list.extend(upstream_hucs)

        return list(OrderedDict((x, True) for x in huc_list).keys())

def get_upstream_hucs(downstream_huc, to_huc_table):
    if downstream_huc:
        huc_upstream_list = [
            d['properties']['HUC12'] for d in to_huc_table if
            d['properties']['ToHUC'] == downstream_huc
        ]

        return huc_upstream_list

def get_upstream_geo(huc2, huc_list, to_huc_table):
    if huc_list:
        huc_upstream_geo = [
            d for d in to_huc_table['objects'][f'{huc2}_HUC12']['geometries'] if
            d['properties']['HUC12'] in huc_list
        ]
        to_huc_table['objects'][f'{huc2}_HUC12']['geometries'] = huc_upstream_geo
        return to_huc_table

def add_hdb_marker(huc_map, row):
        try:
#            site_id = row['site_id']
            obj_type = int(row['site_metadata.objecttype_id'])
            lat = float(row['site_metadata.lat'])
            lon = float(row['site_metadata.longi'])
            elev = row['site_metadata.elevation']
            lat_long = [lat, lon]
            site_name = row['site_metadata.site_name']
#            href = f'./{site_id}/dashboard.html'
#            embed = f'''<div class="container embed-responsive embed-responsive-16by9">
#                  <embed class="embed-responsive-item" src="{href}" scrolling="no" frameborder="0" allowfullscreen></embed>
#                </div>'''

            popup_html = (
#                f'<a href="{href}" target="_blank">OPEN IN NEW WINDOW</a><br>'
#                f'{embed}'
                f'<span class="text-nowrap"><b>{site_name.upper()}</b></span><br>'
                f'<span class="text-nowrap">Latitude: {round(lat, 3)}</span><br>'
                f'<span class="text-nowrap">Longitude: {round(lon, 3)}</span><br>'
                f'<span class="text-nowrap">Elevation: {elev}</span><br>'
            )

            icon = get_fa_icon(obj_type)
            color = get_icon_color(row)
            folium.Marker(
                location=lat_long,
                popup=popup_html,
                tooltip=site_name,
                icon=folium.Icon(icon=icon, prefix='fa', color=color)
            ).add_to(huc_map)
        except (ValueError, TypeError):
            pass

def get_embed(href):
    embed = f'''<div class="container embed-responsive embed-responsive-16by9">
          <embed class="embed-responsive-item" src="{href}" scrolling="no" frameborder="0" allowfullscreen></embed>
        </div>'''
    return embed

def add_awdb_markers(huc_map, meta):
    meta_no_dups = meta.drop_duplicates(subset='stationTriplet')
    for index, row in meta_no_dups.iterrows():
        try:
            site_triplet = row['stationTriplet']
            site_triplet_arr = site_triplet.split(":")
            site_id = site_triplet_arr[0]
            state = site_triplet_arr[1]
            network = site_triplet_arr[2]
            lat = float(row['latitude'])
            lon = float(row['longitude'])
            elev = row['elevation']
            lat_long = [lat, lon]
            site_name = row['name']
            site_href_base = 'https://wcc.sc.egov.usda.gov/nwcc/site?sitenum='
            site_href = f'{site_href_base}{site_id}'
            charts_href_base = 'https://www.nrcs.usda.gov/Internet/WCIS/siteCharts/POR'
            wteq_href = f'{charts_href_base}/WTEQ/{state}/{site_name}.html'
            prec_href = f'{charts_href_base}/PREC/{state}/{site_name}.html'
            tavg_href = f'{charts_href_base}/TAVG/{state}/{site_name}.html'

            popup_html = (
                f'<b><a href="{site_href}" target="_blank">{site_name}</a></b><br>'
                f'<span class="text-nowrap">ID: {site_triplet}</span><br>'
                f'<span class="text-nowrap">Latitude: {round(lat, 3)}</span><br>'
                f'<span class="text-nowrap">Longitude: {round(lon, 3)}</span><br>'
                f'<span class="text-nowrap">Elevation: {elev}</span><br>'
#                f'{get_embed(wteq_href)}<br>'
                f'<a href="{wteq_href}" target="NRCS DATA">Snow Chart</a><br>'
                f'<a href="{prec_href}" target="NRCS DATA">Precip. Chart</a><br>'
                f'<a href="{tavg_href}" target="NRCS DATA">Temp. Chart</a><br>'

            )

            icon = 'snowflake-o'
            color = 'red'
            if network == 'SCAN':
                icon = 'umbrella'
                color = f'light{color}'
            folium.Marker(
                location=lat_long,
                popup=popup_html,
                tooltip=site_name,
                icon=folium.Icon(icon=icon, prefix='fa', color=color)
            ).add_to(huc_map)
        except (ValueError, TypeError):
            pass

def get_snotels(geo_df, snow_meta):
    snotels = []
    for i, snotel in snow_meta.iterrows():
        for idx, row in geo_df.iterrows():
            polygon = row['geometry']
            point = Point(snotel['longitude'], snotel['latitude'])
            if polygon.contains(point):
                snotels.append(snotel['stationTriplet'])
    return snow_meta[snow_meta['stationTriplet'].isin(snotels)]

def get_snow_meta(snow_meta_url=None):
    if not snow_meta_url:
        snow_meta_url = r'https://www.nrcs.usda.gov/Internet/WCIS/sitedata/metadata/ALL/metadata.json'
    snow_meta = pd.read_json(snow_meta_url)
    return snow_meta

def combine_polygons(geo_df, huc_name):
    polygons = geo_df['geometry']
    geometry = gpd.GeoSeries(cascaded_union(polygons))
    df = pd.DataFrame({'Name': [huc_name]})
    return gpd.GeoDataFrame(df, geometry=geometry)

def get_buffer_geojson(geo_df, snow_meta, buffer):
    geo_df.geometry = geo_df['geometry'].buffer(buffer)
    return json.loads(geo_df.to_json())

def define_buffer(geo_df, snow_meta, min_snotels=3, max_buffer=0.3):
    snow_sites_cnt = 0
    buffer = 0
    snow_sites = []
    while snow_sites_cnt < min_snotels and buffer < max_buffer:
        buffer += 0.05
        buffer_geojson= get_buffer_geojson(
            deepcopy(geo_df),
            snow_meta,
            buffer
        )
        snotels = get_snotels(geo_df, snow_meta)
        snow_sites = snotels[snotels['stationTriplet'].str.contains('|'.join(['SNTL', 'SCAN'])).any(level=0)]
        snow_sites_cnt = len(snow_sites)
    print(f'      {snow_sites_cnt} snotels using a {round(buffer, 2)} deg buffer')
    return buffer_geojson, snow_sites

def add_upstream_layer(huc_map, huc_geojson, buffer_geojson):
    folium.Choropleth(
        name='Upstream Basin Buffer',
        geo_data=buffer_geojson,
        fill_color='blue',
        fill_opacity=0.075,
        line_color='blue',
        line_opacity=0.15,
    ).add_to(huc_map)

    folium.Choropleth(
        name='Upstream Basin',
        geo_data=huc_geojson,
        fill_color='black',
        fill_opacity=0.3,
        line_color='black',
        line_opacity=0.75,
    ).add_to(huc_map)

def create_huc_maps(hdb_meta, site_type_dir):
    this_dir = path.dirname(path.realpath(__file__))
    gis_path = path.join(this_dir, 'gis')
    hdb_meta.drop_duplicates(subset='site_id', inplace=True)
    hdb_meta['site_metadata.lat'] = clean_coords(hdb_meta['site_metadata.lat'])
    hdb_meta['site_metadata.longi'] = clean_coords(hdb_meta['site_metadata.longi'], True)
    snow_meta = get_snow_meta()
    huc2_list = [str(i) for i in [10, 11, 13, 14, 15, 16, 17, 18]]
    huc12_geo_dfs = {}
    huc12_geo_dicts = {}
    topo_huc2_path = path.join(gis_path, 'HUC2.topojson')
    huc2_geo_df = gpd.read_file(topo_huc2_path)
    for huc2 in huc2_list:
        topo_huc12_path = path.join(gis_path, f'{huc2}_HUC12.topojson')
        huc12_geo_dfs[huc2] = gpd.read_file(topo_huc12_path)
        with open(topo_huc12_path) as f:
            huc12_geo_dicts[huc2] = json.load(f)

    for idx, row in hdb_meta.iterrows():
        site_name = row['site_metadata.site_name']
        print(f'    Creating map for {site_name}...')
        site_id = row['site_id']
        lat = float(row['site_metadata.lat'])
        lon = float(row['site_metadata.longi'])
        lat_long = [lat, lon]
        huc12 = row['site_metadata.hydrologic_unit']
        huc_map = folium.Map(
            tiles='Stamen Terrain',
            location=lat_long,
            zoom_start=9
        )
        add_hdb_marker(huc_map, row)
        if not huc12 or len(str(huc12)) < 12:
            huc2 = get_huc(huc2_geo_df, lat, lon, level='2')
            if huc2 and huc2 in huc2_list:
                huc12 = get_huc(huc12_geo_dfs[huc2], lat, lon, level='12')

        if str(huc12).isnumeric():
            huc12 = str(huc12)
            huc2 = huc12[:2]
            huc_dict = deepcopy(huc12_geo_dicts[huc2])
            upstream_huc_list = get_upstream_basin(huc12, huc_dict)
            geo_df = huc12_geo_dfs[huc2]
            geo_df = geo_df[geo_df['HUC12'].isin(upstream_huc_list)]
            geo_df = combine_polygons(geo_df, site_name)
            huc_geojson = json.loads(geo_df.to_json())
            buffer_geojson, snow_sites = define_buffer(geo_df, snow_meta)
            add_upstream_layer(huc_map, huc_geojson, buffer_geojson)
            add_awdb_markers(huc_map, snow_sites)
            bounds_list = geo_df['geometry'][0].bounds
            bounds = [
                (bounds_list[1], bounds_list[0]),
                (bounds_list[3], bounds_list[2])
            ]
            if bounds:
                huc_map.fit_bounds(bounds)
        
        add_huc_layer(huc_map, 2)
        add_huc_layer(huc_map, 6) 
        add_optional_tilesets(huc_map)
        folium.LayerControl().add_to(huc_map)
        FloatImage(
            get_bor_seal(orient='shield'),
            bottom=1,
            left=1
        ).add_to(huc_map)
        MousePosition(prefix="Location: ").add_to(huc_map)
        maps_dir = path.join(site_type_dir, f'{site_id}', 'maps')
        makedirs(maps_dir, exist_ok=True)
        map_path = path.join(maps_dir,f'{site_id}_huc.html')
        huc_map.save(map_path)
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

    return f'   Created HUC maps for {site_type_dir} successfully'

if __name__ == '__main__':
    print('very weak test to follow...')
    this_dir = path.dirname(path.realpath(__file__))
    maps_dir = path.join(this_dir, 'test', 'huc_maps')
    makedirs(maps_dir, exist_ok=True)
    site_type_dir = path.join(this_dir, 'test', 'data')
    meta_path = path.join(site_type_dir, 'meta.csv')
#    site_type_dir = path.join(this_dir, 'flat_files', 'ECO_RESERVOIR_DATA')
#    meta_path = path.join(site_type_dir, 'meta.csv')
    hdb_meta = pd.read_csv(meta_path)
#    use_obj_types = [7]
#    hdb_meta = hdb_meta[
#        hdb_meta['site_metadata.objecttype_id'].isin(use_obj_types)
#    ]
    create_huc_maps(hdb_meta, site_type_dir)

