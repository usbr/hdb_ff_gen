# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 08:14:46 2019

@author: buriona
"""

from collections import OrderedDict
import folium
import pandas as pd
from requests import get as req_get
from os import path, makedirs
from copy import deepcopy
import geopandas as gpd
import json
from shapely.geometry import Point
from shapely.ops import cascaded_union
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

def get_bounds(lats, longs):
    max_lat = max(lats)
    max_long = -1 * max([abs(i) for i in longs])
    min_lat = min(lats)
    min_long = -1 * min([abs(i) for i in longs])
    return [(min_lat, max_long), (max_lat, min_long)]

def add_hdb_marker(huc_map, row):
        try:
#            site_id = row['site_id']
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

            icon = 'tint'
            folium.Marker(
                location=lat_long,
                popup=popup_html,
                tooltip=site_name,
                icon=folium.Icon(icon=icon, prefix='fa', color='blue')
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
#            network = site_triplet_arr[2]
            lat = float(row['latitude'])
            lon = float(row['longitude'])
            elev = row['elevation']
            lat_long = [lat, lon]
            site_name = row['name']
            site_href_base = 'https://wcc.sc.egov.usda.gov/nwcc/site?sitenum='
            site_href = f'{site_href_base}{site_id}'
            charts_href_base = 'https://www.nrcs.usda.gov/Internet/WCIS/siteCharts/POR/'
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
                f'<a href="{wteq_href}" target="_blank">Snow Chart</a><br>'
                f'<a href="{prec_href}" target="_blank">Precip. Chart</a><br>'
                f'<a href="{tavg_href}" target="_blank">Temp. Chart</a><br>'

            )

            icon = 'umbrella'
            folium.Marker(
                location=lat_long,
                popup=popup_html,
                tooltip=site_name,
                icon=folium.Icon(icon=icon, prefix='fa', color='green')
            ).add_to(huc_map)
        except (ValueError, TypeError):
            pass

def combine_polygons(geo_df, huc_name):
    polygons = geo_df['geometry']
    geometry = gpd.GeoSeries(cascaded_union(polygons))
    df = pd.DataFrame({'Name': [huc_name]})
    return gpd.GeoDataFrame(df, geometry=geometry)

def get_buffer_geojson(geo_df, snow_meta, buffer):
    geo_df.geometry = geo_df['geometry'].buffer(buffer)
    return json.loads(geo_df.to_json())

def get_snotels(geo_df, snow_meta):
    snotels = []
    for i, snotel in snow_meta.iterrows():
        for idx, row in geo_df.iterrows():
            polygon = row['geometry']
            point = Point(snotel['longitude'], snotel['latitude'])
            if polygon.contains(point):
                snotels.append(snotel['stationTriplet'])
    return snow_meta[snow_meta['stationTriplet'].isin(snotels)]

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
        snow_sites = snotels[snotels['stationTriplet'].str.contains('SNTL')]
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
        style_function = huc6_style
    ).add_to(huc_map)

def get_snow_meta(snow_meta_url=None):
    if not snow_meta_url:
        snow_meta_url = r'https://www.nrcs.usda.gov/Internet/WCIS/sitedata/metadata/WTEQ/metadata.json'
    snow_meta = pd.read_json(snow_meta_url)
    return snow_meta

def create_huc_maps(hdb_meta, site_type_dir):
    this_dir = path.dirname(path.realpath(__file__))
    gis_path = path.join(this_dir, 'gis')
    hdb_meta.drop_duplicates(subset='site_id', inplace=True)
    snow_meta = get_snow_meta()
#    huc2_geo_df = gpd.read_file(r'./gis/HUC2.topojson')
    huc2_list = [str(i) for i in [10, 11, 13, 14, 15, 16, 17, 18]]
#    huc6_topo_path = path.join(this_dir, 'gis', 'HUC6.topojson')
#    with open(huc6_topo_path) as f:
#        huc6_topojson = json.load(f)
    huc12_geo_dfs = {}
    huc12_geo_dicts = {}
    for huc2 in huc2_list:

        topo_json_path = path.join(gis_path, f'{huc2}_HUC12.topojson')
        huc12_geo_dfs[huc2] = gpd.read_file(topo_json_path)
        with open(topo_json_path) as f:
            huc12_geo_dicts[huc2] = json.load(f)

    for idx, row in hdb_meta.iterrows():

        huc12 = row['site_metadata.hydrologic_unit']
        site_name = row['site_metadata.site_name']
        site_id = row['site_id']
        print(f'    Creating map for {site_name}...')
        lat = float(row['site_metadata.lat'])
        lon = float(row['site_metadata.longi'])
        lat_long = [lat, lon]
        huc_map = folium.Map(
            tiles='Stamen Terrain',
            location=lat_long,
            zoom_start=9
        )
        add_hdb_marker(huc_map, row)

        if huc12:
            huc12 = str(huc12)
            huc2 = huc12[:2]
            huc_dict = deepcopy(huc12_geo_dicts[huc2])
            upstream_huc_list = get_upstream_basin(huc12, huc_dict)
    #        huc_topojson = get_upstream_geo(huc2, upstream_huc_list, huc_dict)
            geo_df = huc12_geo_dfs[huc2]
            geo_df = geo_df[geo_df['HUC12'].isin(upstream_huc_list)]
            geo_df = combine_polygons(geo_df, site_name)
            huc_geojson = json.loads(geo_df.to_json())
            buffer_geojson, snow_sites = define_buffer(geo_df, snow_meta)
            huc6_path = path.join(gis_path, 'HUC6.geojson')
            add_hu6_layer(huc_map, huc6_path, True)
            add_upstream_layer(huc_map, huc_geojson, buffer_geojson)
            add_awdb_markers(huc_map, snow_sites)
            lats = snow_sites['latitude'].to_list() + [lat]
            longs = snow_sites['longitude'].to_list() + [lon]
            bounds = get_bounds(lats, longs)
            if bounds:
                huc_map.fit_bounds(bounds)

            folium.LayerControl().add_to(huc_map)
        maps_dir = path.join(site_type_dir, f'{site_id}', 'maps')
        makedirs(maps_dir, exist_ok=True)
        huc_map.save(
            path.join(maps_dir,f'{site_id}_huc.html')
        )
    return f'   Created HUC maps for {site_type_dir} successfully'

if __name__ == '__main__':
    print('very weak test to follow...')
    this_dir = path.dirname(path.realpath(__file__))
    maps_dir = path.join(this_dir, 'test', 'huc_maps')
    makedirs(maps_dir, exist_ok=True)
    meta_path = path.join(this_dir, 'test', 'data', 'test_hdb_metadata.csv')
    site_type_dir = path.join(this_dir, 'flat_files', 'ECO_RESERVOIR_DATA')
    meta_path = path.join(site_type_dir, 'meta.csv')
    hdb_meta = pd.read_csv(meta_path)
#    use_obj_types = [7]
#    hdb_meta = hdb_meta[
#        hdb_meta['site_metadata.objecttype_id'].isin(use_obj_types)
#    ]
    create_huc_maps(hdb_meta, site_type_dir)

