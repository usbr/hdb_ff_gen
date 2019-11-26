# -*- coding: utf-8 -*-
"""
Created on Wed May  1 09:42:27 2019

@author: buriona
"""

from datetime import datetime as dt
from datetime import date
import pandas as pd
import numpy as np
import plotly
import plotly.graph_objs as go
from ff_utils import get_favicon, get_bor_seal
from hdb_api.hdb_utils import datatype_units, get_wy, is_leap_year, get_cal_yr

def get_log_scale_dd():
    log_scale_dd = [
        {
            'active': 0,
            'showactive': True,
            'x': 1.005,
            'y': -0.025,
            'xanchor': 'left',
            'yanchor': 'top',
            'bgcolor': 'rgba(0,0,0,0)',
            'type': 'buttons',
            'direction': 'down',
            'font': {
                'size': 10
            },
            'buttons': [
                {
                    'label': 'Linear Scale',
                    'method': 'relayout',
                    'args': ['yaxis', {'type': 'linear'}]
                },
                {
                    'label': 'Log Scale',
                    'method': 'relayout',
                    'args': ['yaxis', {'type': 'log'}]
                },
            ]
        }
    ]
    return log_scale_dd

def get_chart_type(datatype_name, units):
    if units in ['ACRE-FT'] and 'storage' not in datatype_name:
        return 'bar'
    return 'scatter'

def interp_leap_year_data(df, idx_year=2004):
    feb28 = dt(idx_year, 2, 28)
    feb29 = dt(idx_year, 2, 29)
    mar1 = dt(idx_year, 3, 1)
    df_interp = df.copy()
    for yr in df.columns:
        if not is_leap_year(yr):
            feb28_val = df_interp.at[feb28, yr]
            mar1_val = df_interp.at[mar1, yr]
            df_interp.at[feb29, yr] = round((feb28_val + mar1_val) / 2, 2)
    return df_interp

def bar_stat_shading(x, y, days=14):
    width = pd.Timedelta(days=days)
    x = x.to_list()
    x = [[i - width, i - width, i + width, i + width] for i in x]
    x = [j for k in x for j in k]
    y = [[0, i, i, 0] for i in y]
    y = [j for k in y for j in k]

    return x, y

def stats_shaded_trace(x, y, name, color, chart_type):
    showlegend = False
    name = f'{name}_stats'
    fill = 'tonexty'
    shape = 'linear'
    if chart_type == 'bar':
        shape = 'vh'
        x, y = bar_stat_shading(x, y)
    if 'MIN' in name.upper():
        fill = 'none'
        if chart_type == 'bar':
            fill = 'tozeroy'

#    if 'MEDIAN' in name:
#        showlegend = True
#        name = 'STATS'

    trace = go.Scatter(
        x=x,
        y=y,
        name=name,
        visible=True,
        fill=fill,
        line=dict(
            width=0,
            shape=shape
        ),
        fillcolor=color.replace(',0.5)', ',0.1)'),
        hoverinfo='none',
        legendgroup='stat_traces',
        connectgaps=True,
        showlegend=showlegend,
        stackgroup='stats',
        orientation='h'
    )
    return trace

def scatter_trace(x, y, show_trace, name, color=None, linetype='solid'):
    trace = go.Scatter(
        x=x,
        y=y,
        name=name,
        visible=show_trace,
        line=dict(
            color=color,
            dash=linetype
        )
    )
    return trace

def bar_trace(x, y, show_trace, name, color=None):
    trace = go.Bar(
        x=x,
        y=y,
        name=name,
        visible=show_trace,
        marker=dict(
            color=color
        )
    )
    return trace

def serial_to_wy(df, val_col, dt_col='datetime'):
    df['wy'] = df[dt_col].apply(lambda x: get_wy(x))
    water_years = [x for x in range(df['wy'].min(), df['wy'].max() + 1)]
    days_list = pd.date_range(
        start='2003-10-01',
        end='2004-09-30'
    )

    df_out = pd.DataFrame(index=days_list)
    for wy in water_years:
        idx = pd.date_range(date(wy - 1, 10, 1), date(wy, 9, 30))
        df_wy = df[df['wy'] == wy][val_col]
        df_wy = df.reindex(idx)
        df_wy.drop(columns=[dt_col, 'wy'], inplace=True)
        wy_data = df_wy.values
        if not is_leap_year(wy):
            wy_data = np.insert(wy_data, 151, np.nan)
        df_out[wy] = wy_data

    return df_out

def create_wy_traces(df, datatype_name, units):
    curr_wy = get_wy(dt.now())
    visible = {True:True, False:'legendonly'}
    traces = []
    water_years = df.columns.tolist()
    for wy in water_years:
        color = None
        if str(wy) == str(curr_wy):
            color = 'rgb(0,0,0)'
        df_temp = df[wy]
        x_vals = df_temp.index
        y_vals = df_temp.values
        show_trace = visible[wy in [curr_wy, curr_wy - 1]]
        if get_chart_type(datatype_name, units) == 'bar':
            trace = bar_trace(x_vals, y_vals, show_trace, f'{wy}', color)
        else:
            trace = scatter_trace(x_vals, y_vals, show_trace, f'{wy}', color)
        traces.append(trace)

    return traces

def create_stat_traces(df, datatype_name, units):
    color_dict = {
        'min': 'rgba(255,36,57,0.5)',
        '90%': 'rgba(48,204,255,0.5)',
        '70%': 'rgba(46,255,166,0.5)',
        '50%': 'rgba(63,255,43,0.5)',
        '30%': 'rgba(204,255,40,0.5)',
        '10%': 'rgba(255,161,38,0.5)',
        'max': 'rgba(50,68,255,0.5)',
        'mean': 'rgba(63,255,43,0.5)'
    }
    line_types = {'mean': 'dash', '50%': 'dot'}
    traces = []
#        go.Scatter(
#            x=[df.index],
#            y=[df['50%'].values],
#            name='SHADING',
#            fill='none',
#            visible='legendonly',
#            line=dict(width=0),
#            hoverinfo='none',
#            legendgroup='stat_traces',
#            showlegend=True,
#        )
#    ]

    df.drop(columns=['count', 'std'], inplace=True)
    cols = df.columns.tolist()
    for col in cols:
        color = color_dict.get(col, 'rgba(0,0,0,0.5)')
        linetype = line_types.get(col, 'dashdot')
        df_temp = df[col]
        x_vals = df_temp.index
        y_vals = df_temp.values
        show_trace = 'legendonly'
        trace_name = f'{col.upper()}'
        if '%' in col:
            exceedance = 100 - int(col.replace('%', ''))
            trace_name = f'{exceedance}%'
            if '50' in col:
                trace_name = 'MEDIAN'
        chart_type = get_chart_type(datatype_name, units)
        if chart_type == 'bar':
            if col in ['min', '90%', '70%', '50%', '30%', '10%', 'max']:
                stats_trace = stats_shaded_trace(
                    x_vals,
                    y_vals,
                    trace_name,
                    color,
                    chart_type
                )
                traces.append(stats_trace)
            trace = bar_trace(
                x_vals,
                y_vals,
                show_trace,
                trace_name,
                color
            )
        else:
            if col in ['min', '90%', '70%', '50%', '30%', '10%', 'max']:
                stats_trace = stats_shaded_trace(
                    x_vals,
                    y_vals,
                    trace_name,
                    color,
                    chart_type
                )
                traces.append(stats_trace)

            trace = scatter_trace(
                x_vals,
                y_vals,
                show_trace,
                trace_name,
                color,
                linetype
            )
        traces.append(trace)
    return traces

def get_anno_text(df, df_stats, units):
    curr_wy = max(df.columns)
    last_row = df.loc[df[curr_wy].last_valid_index()]
    curr_month = last_row.name.month
    curr_cal_yr = get_cal_yr(curr_month, curr_wy)
    last_date = f'{last_row.name.strftime("%b %d")}, {curr_cal_yr}'
    last_data = round(last_row.iloc[-1], 2)
    last_year_data = round(last_row.iloc[-2], 2)
    stats_row = df_stats.loc[last_row.name]
    avg_data = stats_row['mean']
    median_data = stats_row['50%']

    if avg_data > 0:
        percent_avg = f'{round(100 * last_data / avg_data, 0):.0f}'
    else:
        percent_avg = 'N/A'

    if median_data > 0:
        percent_median = f'{round(100 * last_data / median_data, 0):.0f}'
    else:
        percent_median = 'N/A'

    if last_year_data > 0:
        percent_last_year = f'{round(100 * last_data / last_year_data, 0):.0f}'
    else:
        percent_last_year = 'N/A'

    last_data_str = f'{last_data:0,.0f}'
    if last_data > 1000000:
        last_data_str = f'{last_data / 1000:0,.2f} K'


    anno_text = (
        f'As of: {last_date}:<br>'
        f'Currently: {last_data_str} {units}<br>'
        f"% Avg. ('81-'10): {percent_avg}%<br>"
        f"% Median ('81-'10): {percent_median}%<br>"
        f'% Last Year: {percent_last_year}%'
    )
    return anno_text

def create_chart(df, meta):
    tickformat = {'scatter': '%m/%d', 'bar': '%B'}
    tick0 = {'scatter': '2003-10-01', 'bar': '2003-10-31'}

    site_name = meta['site_metadata.site_name'].upper()
    datatype_name = meta['datatype_metadata.datatype_common_name']
    datatype_str = datatype_name.upper()
    datatype_id = meta['datatype_id']
    units = datatype_units.get(datatype_id, 'UNKNOWN UNITS').upper()

    df_wy = serial_to_wy(df, datatype_name)
    chart_type = get_chart_type(datatype_name, units)
    if chart_type == 'bar':
        df_wy = df_wy.resample('1M').sum(min_count=25)
    df_wy.dropna(axis='columns', how='all', inplace=True)
    percentiles = [0.10, 0.30, 0.50, 0.70, 0.90]
    df_30yr = df_wy.filter(items=range(1980, 2011), axis='columns')
    if get_chart_type(datatype_name, units) == 'scatter':
        df_30yr = interp_leap_year_data(df_30yr)
    df_30yr = df_30yr.transpose()
    stats_30yr = df_30yr.describe(percentiles=percentiles).transpose()

    traces = create_wy_traces(df_wy, datatype_name, units)
    stat_traces = create_stat_traces(stats_30yr, datatype_name, units)

    traces = traces + stat_traces

    seal_image = [{
        'source': get_bor_seal(orient='shield'),
        'xref': 'paper',
        'yref': 'paper',
        'x': 0.01,
        'y': 1.00,
        'sizex': 0.135,
        'sizey': 0.3,
        'yanchor': 'top',
        'xanchor': 'left',
        'opacity': 0.25,
        'layer': 'below'
    }]

    annotation = [
        {
            'x': 1,
            'y': -0.2,
            'xref': 'paper',
            'yref': 'paper',
            'text': f"Created: {dt.utcnow().strftime('%x %I:%M %p UTC')}",
            'showarrow': False,
            'align': 'left',
            'yanchor': 'top',
            'xanchor': 'right',
            'font': {'size': 8, 'color':'rgba(0,0,0,0.3)'}
        }
    ]

    if not stats_30yr.dropna().empty:
        anno_text = get_anno_text(df_wy, stats_30yr, units)
        annotation.append(
            {
                'x': 1,
                'y': 1.04,
                'xref': 'paper',
                'yref': 'paper',
                'text': anno_text,
                'showarrow': False,
                'align': 'left',
                'yanchor': 'top',
                'xanchor': 'right',
                'bordercolor': 'black',
                'borderpad': 5,
                'bgcolor': 'rgba(255,255,255,0.3)',
                'font': {'size': 10}
            }
        )

    layout = go.Layout(
        template='plotly_white',
        title=(
            f'{site_name} - '
            f'{datatype_str} ({units})'
        ),
        autosize=True,
        annotations=annotation,
        images=seal_image,
        yaxis=dict(
            title=f'{datatype_str} ({units})',
        ),
        xaxis=dict(
            type='date',
            tickformat=tickformat[chart_type],
            dtick="M1",
            tick0=tick0[chart_type],
            rangeslider=dict(thickness=0.1)
        ),
        legend={
            'orientation': 'v'
        },
        margin=go.layout.Margin(
            l=50,
            r=50,
            b=50,
            t=50,
            pad=5
        ),
        updatemenus=get_log_scale_dd()
    )

    fig = go.Figure(
        data=traces,
        layout=layout
    )
    return fig

if __name__ == '__main__':
    from os import path

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

    def make_chart(df, meta, chart_filename, img_filename, plotly_js=None):
        if not plotly_js:
            plotly_js = (
                r'https://www.usbr.gov/uc/water/ff/static/js/plotly/1.48.2/plotly-latest.min.js'
            )
        if True:#try:
            fig = create_chart(df.copy(), meta)
            plotly.offline.plot(
                fig,
                include_plotlyjs=plotly_js,
                config=get_plot_config(img_filename),
                filename=chart_filename,
                auto_open=False,
                validate=False
            )

            flavicon = (
                f'<link rel="shortcut icon" '
                f'href="{get_favicon()}"></head>'
            )
            with open(chart_filename, 'r') as html_file:
                chart_file_str = html_file.read()

            with open(chart_filename, 'w') as html_file:
                html_file.write(chart_file_str.replace(r'</head>', flavicon))

#        except Exception as err:
#            err_str = (
#                f'     Error creating chart - {chart_filename} - {err}'
#            )
#            print(err_str)

    site_id = 731
    sdi = 1332
    datatype_id = 19
    this_dir = path.dirname(path.realpath(__file__))
    test_dir = path.join(this_dir, 'test')
    data_dir = path.join(test_dir, 'data')
    site_dir = path.join(data_dir, f'{site_id}')
    chart_dir = path.join(site_dir, 'charts')
    csv_path = path.join(site_dir, 'csv', f'{datatype_id}.csv')
    meta_path = path.join(data_dir, 'gauge_meta.csv')
    if path.exists(csv_path) and path.exists(meta_path):
        df_meta = pd.read_csv(meta_path)
        meta = df_meta[df_meta['site_datatype_id'] == sdi].iloc[0]
        df = pd.read_csv(
            csv_path,
            parse_dates=['datetime'],
            infer_datetime_format=True
        )
        df.index = df['datetime']
        datatype_label = 'datatype_metadata.datatype_common_name'
        datatype_names = meta[datatype_label]
        chart_filename = path.join(chart_dir, f'{datatype_names}.html')
        img_filename = f'917_{datatype_names}'
        make_chart(df, meta, chart_filename, img_filename)
        print(f'Created {chart_filename}')
    else:
        print(f'No data for site id: {site_id}, please create csv files first')
