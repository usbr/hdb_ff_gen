# -*- coding: utf-8 -*-
"""
Created on Fri Sep 13 15:26:04 2019

@author: buriona
"""

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

if __name__ == '__main__':
    print('Just a utility module')