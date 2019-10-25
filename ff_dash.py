# -*- coding: utf-8 -*-
"""
Created on Wed May 22 12:08:25 2019

@author: buriona
"""

from pathlib import Path, PurePath
from ff_utils import get_favicon, get_bor_seal, get_bootstrap
from hdb_api.hdb_utils import datatype_units, datatype_common_names

label_unit_dict = {
    datatype_common_names[i]: datatype_units[i] for i in datatype_units.keys()
}

datatype_common_names_rev = {v: k for k, v in datatype_common_names.items()}

bor_flavicon = get_favicon()
bor_seal = get_bor_seal()
bootstrap = get_bootstrap()
bootstrap_css = bootstrap['css']
bootstrap_js = bootstrap['js']
jquery_js = bootstrap['jquery']
feather_js = r'https://www.usbr.gov/uc/water/ff/static/js/feather.min.js'
dashboard_css = r'https://www.usbr.gov/uc/water/ff/static/css/custom/dashboard.css'

def get_feather(datatype_name):
    units = label_unit_dict.get(datatype_name, 'UNKNOWN UNITS').lower()
    if units in ['acre-ft'] and 'storage' not in datatype_name.lower():
        return 'bar-chart-2'
    elif units == 'UNKNOWN UNITS':
        return 'chevron-right'
    return 'trending-up'

def get_datatype_units(datatype_id, datatype_units_dict):
    units = datatype_units_dict.get(datatype_id, 'UNKNOWN UNITS')
    return units

def get_site_url():
    return 'https://www.usbr.gov/uc/water/index.html'

def get_home_url():
    return r'../../ff_nav.html'

def get_map_url():
    return r'../site_map.html'

def create_sidebar_link(chart_name, feather):
    jumpto = chart_name.replace(' ', '_')
    label = jumpto.title().replace("_", " ")
    link = f'''          <li class="nav-item">
            <a class="nav-link" data-toggle="tab" href="#{jumpto}" role="tab">
            <span data-feather="{feather}"></span>  {label}</a>
          </li>'''
    return link

def get_map_navbar_link(site_id):
    navbar_link = f'''
          <li class="nav-item">
            <a class="nav-link active" data-toggle="tab" href="#huc" role="tab">
            <span data-feather="map"></span>  Upstream Map</a>
          </li>'''
    return navbar_link

def get_chart_navbar_links(chart_names):
    navbar_links = []
    for chart_name in chart_names:
        feather = get_feather(chart_name.replace('_', ' '))
        navbar_links.append(create_sidebar_link(chart_name, feather))
    return '\n'.join(navbar_links)

def create_map_embed(site_id):
    embed = f'''          <div id="huc" class="tab-pane active show fade in embed-responsive embed-responsive-16by9" role="tabpanel">
            <embed class="embed-responsive-item" src="./maps/{site_id}_huc.html"></embed>
          </div>'''
    return embed

def create_embed(chart_name):
    jumpto = chart_name.replace(' ', '_')
    embed = f'''          <div id="{jumpto}" class="tab-pane fade in embed-responsive embed-responsive-16by9" role="tabpanel">
            <embed class="embed-responsive-item" src="./charts/{chart_name}.html"></embed>
          </div>'''
    return embed

def get_embeds(chart_names):
    embeds = []
    for chart_name in chart_names:
        embeds.append(create_embed(chart_name))
    return '\n'.join(embeds)

def create_data_link(chart_name, file_type):
    data_type = datatype_common_names_rev.get(
        chart_name.replace('_', ' '),
        'UNKNOWN DATA TYPE'
    )
    ext = file_type.lower()
    label = chart_name.title().replace('_', ' ')
    return f'''                <a href="./{ext}/{data_type}.{ext}">
                  <li class="list-group-item d-flex justify-content-between align-items-center">{label}
                    <span class="badge badge-primary badge-pill">{ext}</span>
                  </li>
                </a>'''

def get_data_div(chart_names, file_type):
    jumpto = file_type.lower()
    prefix = f'''
          <div id="{jumpto}" class="tab-pane fade in col-sm-4 col-md-3 m-5" role="tabpanel">
            <embed class="embed-responsive-item">
              <ul class="list-group">
'''
    data_div = []
    for chart_name in chart_names:
        data_div.append(create_data_link(chart_name, file_type))
    body = '\n'.join(data_div)
    return f'''{prefix}{body}
              </ul>
            </embed>
          </div>'''

def get_dash_head():
    return f'''
<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="{bor_flavicon}">
  <link rel="stylesheet" href="{bootstrap_css}">
  <link rel="stylesheet" href="{dashboard_css}">
</head>
'''

def get_js_refs():
    return (f'''
<!-- Bootstrap core JavaScript
================================================== -->
<!-- Placed at the end of the document so the pages load faster -->
  <script src="{jquery_js}"></script>
  <script src="{bootstrap_js}"></script>
''' + f'''
<!-- Icons -->
  <script src="{feather_js}"></script>
  <script>
    feather.replace()
  </script>
''' + '''
<!-- to enable link to tab -->
  <script>
    $(document).ready(() => {
      let url = location.href.replace(/\/$/, "");

      if (location.hash) {
        const hash = url.split("#");
        $('#navTabs a[href="#'+hash[1]+'"]').tab("show");
        url = location.href.replace(/\/#/, "#");
        history.replaceState(null, null, url);
        setTimeout(() => {
          $(window).scrollTop(0);
        }, 400);
      }

      $('a[data-toggle="tab"]').on("click", function() {
        let newUrl;
        const hash = $(this).attr("href");
        if(hash == "#home") {
          newUrl = url.split("#")[0];
        } else {
          newUrl = url.split("#")[0] + hash;
        }
        newUrl += "/";
        history.replaceState(null, null, newUrl);
      });
    });
  </script>'''
)

def get_dash_body(site_name, site_id, chart_names):
    return f'''
<body>
<nav class="navbar navbar-light fixed-top bg-light navbar-expand p-auto flex-md-nowrap">
  <a class="btn btn-outline-primary" target="_blank" href="#huc">{site_name}</a>
  <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav">
  <span class="navbar-toggler-icon"></span>
  </button>
  <div class="collapse navbar-collapse" id="navbarNav">
    <ul class="navbar-nav  mr-auto">
      <li class="nav-item">
        <a class="nav-link ml-3" href="{get_map_url()}">Overview Map</a>
        </li>
      <li class="nav-item">
        <a class="nav-link ml-3" href="{get_home_url()}l">Navigator</a>
      </li>
    </ul>
  </div>
</nav>
<div class="container-fluid">
  <div class="row">
    <nav class="sidebar col-md-2 mt-2">
      <div class="sidebar-sticky">
        <a class="sidebar-heading d-flex px-3 mt-4 mb-1" href="https://www.usbr.gov/uc/water/index.html">
          <img src="{bor_seal}" class="img-fluid" alt="Reclamation Seal">
        </a>
        <h6 class="sidebar-heading d-flex justify-content-between align-items-center px-3 mt-4 mb-1 text-muted">
          <span>Maps</span>
          <a class="d-flex align-items-center text-muted" href="#">
            <span data-feather="map"></span>
          </a>
        </h6>
        <ul class="nav flex-column nav-tabs" id="navTabs" role="tablist">
         {get_map_navbar_link(site_id)}
         <h6 class="sidebar-heading d-flex justify-content-between align-items-center px-3 mt-4 mb-1 text-muted">
           <span>Charts</span>
           <a class="d-flex align-items-center text-muted" href="#">
             <span data-feather="trending-up"></span>
             <span data-feather="bar-chart-2"></span>
           </a>
         </h6>
         {get_chart_navbar_links(chart_names)}
         <h6 class="sidebar-heading d-flex justify-content-between align-items-center px-3 mt-4 mb-1 text-muted">
           <span>Period of Record Data</span>
           <a class="d-flex align-items-center text-muted" href="#">
             <span data-feather="database"></span>
             <span data-feather="archive"></span>
           </a>
         </h6>
         <li class="nav-item">
           <a class="nav-link" data-toggle="tab" href="#csv" role="tab">
             <span data-feather="database"></span>  CSV DATA</a>
         </li>
         <li class="nav-item">
           <a class="nav-link" data-toggle="tab" href="#json"  role="tab">
             <span data-feather="archive"></span>  JSON DATA</a>
         </li>
        </ul>
      </div>
    </nav>
    <main class="col-md-9 ml-sm-auto col-lg-10 px-1 pt-5">
        <div class="row tab-content m-auto p-auto">
{create_map_embed(site_id)}
{get_embeds(chart_names)}
{get_data_div(chart_names, 'csv')}
{get_data_div(chart_names, 'json')}
        </div>
    </main>
  </div>
</div>

{get_js_refs()}

</body>
</html>
'''

def create_dash(site_name, site_id, site_path):
    chart_dir = Path(site_path, 'charts').resolve()
    chart_paths = chart_dir.iterdir()
    chart_names = [PurePath(x) for x in chart_paths]
    chart_names[:] = [
        x for x in chart_names if x.suffix == '.html'
    ]
    chart_names[:] = [x.name.replace('.html', '') for x in chart_names]
    return f'{get_dash_head()}{get_dash_body(site_name, site_id, chart_names)}'

if __name__ == '__main__':

    import os
    from ff_nav import create_nav
    this_dir = os.path.dirname(os.path.realpath(__file__))
    data_dir = os.path.join(this_dir, 'flat_files')
    sys_out = create_nav(data_dir)
    print(sys_out)