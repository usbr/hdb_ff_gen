# -*- coding: utf-8 -*-
"""
Created on Fri Sep 13 15:26:04 2019

@author: buriona
"""

def get_bor_js():
    return [
        ('leaflet',
         'https://www.usbr.gov/uc/water/ff/static/js/leaflet/leaflet.js'),
        ('jquery',
         'https://www.usbr.gov/uc/water/ff/static/js/jquery/3.4.0/jquery.min.js'),
        ('bootstrap',
         'https://www.usbr.gov/uc/water/ff/static/js/bootstrap/3.2.0/js/bootstrap.min.js'),
        ('awesome_markers',
         'https://www.usbr.gov/uc/water/ff/static/js/leaflet/leaflet.awesome-markers.js'),  # noqa
        ]

def get_bor_css():
    return [
        ('leaflet_css',
         'https://www.usbr.gov/uc/water/ff/static/css/leaflet/leaflet.css'),
        ('bootstrap_css',
         'https://www.usbr.gov/uc/water/ff/static/css/bootstrap/3.2.0/css/bootstrap.min.css'),
        ('bootstrap_theme_css',
         'https://www.usbr.gov/uc/water/ff/static/css/bootstrap/3.2.0/css/bootstrap-theme.min.css'),  # noqa
        ('awesome_markers_font_css',
         'https://www.usbr.gov/uc/water/ff/static/css/font-awesome.min.css'),  # noqa
        ('awesome_markers_css',
         'https://www.usbr.gov/uc/water/ff/static/css/leaflet/leaflet.awesome-markers.css'),  # noqa
        ('awesome_rotate_css',
         'https://www.usbr.gov/uc/water/ff/static/css/leaflet/leaflet.awesome.rotate.css'),  # noqa
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
         'https://www.usbr.gov/uc/water/ff/static/css/font-awesome.min.css'),
         ('awesome_markers_font_css',
         'https://maxcdn.bootstrapcdn.com/font-awesome/4.6.3/css/font-awesome.min.css'),  # noqa
        ('awesome_markers_css',
         'https://cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.css'),  # noqa
        ('awesome_rotate_css',
         'https://rawcdn.githack.com/python-visualization/folium/master/folium/templates/leaflet.awesome.rotate.css'),  # noqa
        ]

if __name__ == '__main__':
    print('Just a utility module')
