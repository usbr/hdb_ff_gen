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
# import numpy as np
#from requests import get as req_get
import geopandas as gpd
from shapely.geometry import Point
from shapely.ops import cascaded_union
from ff_utils import get_fa_icon, get_icon_color, get_season
from ff_utils import add_optional_tilesets, add_huc_layer, clean_coords, get_huc
from ff_utils import get_favicon, get_bor_seal
from ff_utils import get_default_js, get_default_css, NRCS_SITE_CHARTS_URL, NRCS_BASE_URL

default_js = get_default_js()
default_css = get_default_css()
folium.folium._default_js = default_js
folium.folium._default_css = default_css

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
            popup = folium.map.Popup(
                html=popup_html,
                max_width=720
            )
            icon = get_fa_icon(obj_type)
            color = get_icon_color(row)
            folium.Marker(
                location=lat_long,
                popup=popup,
                tooltip=site_name,
                icon=folium.Icon(icon=icon, prefix='fa', color=color)
            ).add_to(huc_map)
        except (ValueError, TypeError):
            pass

def get_embed(href):
    embed = (
        f'<div class="container embed-responsive embed-responsive-4by3" style="overflow: hidden; height: 650px; width: 720px;">'
        f'<iframe class="embed-responsive-item" src="{href}" scrolling="no" frameborder="0" allowfullscreen></iframe>'
        f'</div>'
    )   
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
            charts_href_base = f'{NRCS_SITE_CHARTS_URL}'
            seasonal_href = f'{charts_href_base}/WTEQ/{state}/{site_name.replace("#", "%233")}.html'
            if get_season() == 'summer':
                seasonal_href = f'{charts_href_base}/PREC/{state}/{site_name}.html'

            popup_html = (
                f'<div class="container">'
                f'<div class="row justify-content-center">'
                f'<div class="col">'
                f'<a href="{site_href}" target="_blank">'
                f'<button class="btn btn-primary btn-sm btn-block">'
                f'Courtesy NRCS - Go to {site_name} Site Page...</button></a></div>'
                f'<div class="row justify-content-center">{get_embed(seasonal_href)}</div>'
                f'</div></div>'
            )
            popup = folium.map.Popup(html=popup_html)
            icon = get_fa_icon(network, source='awdb')
            color = get_icon_color(network, source='awdb')
            folium.Marker(
                location=lat_long,
                popup=popup,
                tooltip=site_name,
                icon=folium.Icon(icon=icon, prefix='fa', color=color)
            ).add_to(huc_map)
        except (ValueError, TypeError):
            pass

def get_awdb_sites(geo_df, awdb_meta):
    awdb_sites = []
    for i, awdb_site in awdb_meta.iterrows():
        for idx, row in geo_df.iterrows():
            polygon = row['geometry']
            point = Point(awdb_site['longitude'], awdb_site['latitude'])
            if polygon.contains(point):
                awdb_sites.append(awdb_site['stationTriplet'])
    return awdb_meta[awdb_meta['stationTriplet'].isin(awdb_sites)]

def get_awdb_meta(site_type='WTEQ'):
    url_prefix = f'{NRCS_BASE_URL}/sitedata/metadata'
    awdb_meta_url = f'{url_prefix}/{site_type}/metadata.json'
    awdb_meta = pd.read_json(awdb_meta_url)
    return awdb_meta

def combine_polygons(geo_df, huc_name):
    polygons = geo_df['geometry']
    geometry = gpd.GeoSeries(cascaded_union(polygons))
    df = pd.DataFrame({'Name': [huc_name]})
    return gpd.GeoDataFrame(df, geometry=geometry)

def define_buffer(geo_df, awdb_meta, min_awdb_sites=3, max_buffer=0.3):
    awdb_sites_cnt = 0
    buffer = 0
    awdb_sites = []
    while awdb_sites_cnt < min_awdb_sites and buffer < max_buffer:
        buffer += 0.05
        buffer_df = deepcopy(geo_df)
        buffer_df.geometry = buffer_df['geometry'].buffer(buffer)
        awdb_sites = get_awdb_sites(
            buffer_df, 
            awdb_meta
        )
        awdb_sites = awdb_sites[awdb_sites['stationTriplet'].str.contains('|'.join(['SNTL', 'SCAN'])).any(level=0)]
        awdb_sites_cnt = len(awdb_sites)
    buffer_geojson = json.loads(buffer_df.to_json())
    print(f'      {awdb_sites_cnt} awdb_sites using a {round(buffer, 2)} deg buffer')
    return buffer_geojson, awdb_sites

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
    hdb_meta['site_metadata.longi'] = clean_coords(
        hdb_meta['site_metadata.longi'], force_neg=True
    )
    awdb_site_type = 'WTEQ'
    if get_season() == 'summer':
        awdb_site_type = 'PREC'
    awdb_meta = get_awdb_meta(awdb_site_type)
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
        try:
            site_name = row['site_metadata.site_name']
            print(f'    Creating map for {site_name}...')
            site_id = row['site_id']
            lat = float(row['site_metadata.lat'])
            lon = float(row['site_metadata.longi'])
            huc12 = row['site_metadata.hydrologic_unit']
            huc_map = folium.Map(tiles=None)
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
                buffer_geojson, awdb_sites = define_buffer(geo_df, awdb_meta)
                add_upstream_layer(huc_map, huc_geojson, buffer_geojson)
                add_awdb_markers(huc_map, awdb_sites)
                bounds_list = geo_df['geometry'][0].bounds
                bounds = [
                    (bounds_list[1], bounds_list[0]),
                    (bounds_list[3], bounds_list[2])
                ]
                if bounds:
                    huc_map.fit_bounds(bounds)
            
            # add_huc_layer(huc_map, 2)
            # add_huc_layer(huc_map, 6) 
            add_optional_tilesets(huc_map)
            folium.LayerControl().add_to(huc_map)
            FloatImage(
                get_bor_seal(orient='shield'),
                bottom=1,
                left=1
            ).add_to(huc_map)
            # MousePosition(prefix="Location: ").add_to(huc_map)
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
        
        except Exception as err:
            print(f'     Could not create huc map for {site_name} - {err}')

    return f'   Created HUC maps for {site_type_dir} successfully'

if __name__ == '__main__':
    print('very weak test to follow...')
    this_dir = path.dirname(path.realpath(__file__))
    maps_dir = path.join(this_dir, 'test', 'huc_maps')
    makedirs(maps_dir, exist_ok=True)
    # site_type_dir = path.join(this_dir, 'test', 'data')
    # meta_path = path.join(site_type_dir, 'klamath_meta.csv')
    site_type_dir = path.join(this_dir, 'flat_files', 'gage_data')
    meta_path = path.join(site_type_dir, 'meta.csv')
#    site_type_dir = path.join(this_dir, 'flat_files', 'ECO_RESERVOIR_DATA')
#    meta_path = path.join(site_type_dir, 'meta.csv')
    hdb_meta = pd.read_csv(meta_path)
#    use_obj_types = [7]
#    hdb_meta = hdb_meta[
#        hdb_meta['site_metadata.objecttype_id'].isin(use_obj_types)
#    ]
    create_huc_maps(hdb_meta, site_type_dir)

