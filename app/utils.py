# Modifications to lightkurve interact
# CAN'T USE CALLBACKS IN PYTHON UNLESS SERVER OR NOTEBOOK

import numpy as np
# from bokeh.io import show, output_notebook, push_notebook, output_file
from bokeh.plotting import figure, ColumnDataSource, gridplot
from bokeh.models import LogColorMapper, Selection, Slider, RangeSlider, \
    Span, ColorBar, LogTicker, Range1d
from bokeh.layouts import layout, Spacer, column
from bokeh.models.tools import HoverTool
from bokeh.models.widgets import Button, Div
from bokeh.models.formatters import PrintfTickFormatter
from bokeh.embed import components
from lightkurve.interact import prepare_lightcurve_datasource, prepare_tpf_datasource, get_lightcurve_y_limits


def simple_ui(tpf, ap_mask=None):
    if ap_mask is None:
        ap_mask = tpf.create_threshold_mask()
    lc = tpf.to_lightcurve(aperture_mask=ap_mask)
    lc_source = prepare_lightcurve_datasource(lc)
    tpf_source = prepare_tpf_datasource(tpf, ap_mask)

    lc_fig = make_lc_fig(lc, lc_source)
    tpf_fig = make_tpf_fig(tpf, tpf_source)

    p = gridplot([[lc_fig, tpf_fig]], toolbar_location="left")
    script, div = components(p)

    return script, div

def make_lc_fig(lc, lc_source):
    title = "Lightcurve (TESS Sec. {})".format(lc.sector)

    fig = figure(title=title, plot_height=340, plot_width=600,
                 tools="pan,wheel_zoom,box_zoom,tap,reset",
                 toolbar_location="below",
                 border_fill_color="whitesmoke")
    fig.title.offset = -10
    fig.yaxis.axis_label = 'Flux (e/s)'
    fig.xaxis.axis_label = 'Time (days)'
    fig.xaxis.axis_label = 'Time - 2457000 (days)'

    ylims = get_lightcurve_y_limits(lc_source)
    fig.y_range = Range1d(start=ylims[0], end=ylims[1])

    # Add step lines, circles, and hover-over tooltips
    fig.step('time', 'flux', line_width=1, color='gray',
             source=lc_source, nonselection_line_color='gray',
             nonselection_line_alpha=1.0)
    circ = fig.circle('time', 'flux', source=lc_source, fill_alpha=0.3, size=8,
                      line_color=None, selection_color="firebrick",
                      nonselection_fill_alpha=0.0,
                      nonselection_fill_color="grey",
                      nonselection_line_color=None,
                      nonselection_line_alpha=0.0,
                      fill_color=None, hover_fill_color="firebrick",
                      hover_alpha=0.9, hover_line_color="white")
    tooltips = [("Cadence", "@cadence"),
                ("Time ({})".format(lc.time_format.upper()),
                 "@time{0,0.000}"),
                ("Time (ISO)", "@time_iso"),
                ("Flux", "@flux"),
                ("Quality Code", "@quality_code"),
                ("Quality Flag", "@quality")]
    fig.add_tools(HoverTool(tooltips=tooltips, renderers=[circ],
                            mode='mouse', point_policy="snap_to_data"))

    return fig

def make_tpf_fig(tpf, tpf_source, pedestal=0, fiducial_frame=800,
                             plot_width=370, plot_height=340):
    title = 'Pixel data (Camera {}.{})'.format(tpf.camera, tpf.ccd)
    fig = figure(plot_width=plot_width, plot_height=plot_height,
                 x_range=(tpf.column, tpf.column + tpf.shape[2]),
                 y_range=(tpf.row, tpf.row + tpf.shape[1]),
                 title=title, tools='tap,box_select,wheel_zoom,reset',
                 toolbar_location="below",
                 border_fill_color="whitesmoke")

    fig.yaxis.axis_label = 'Pixel Row Number'
    fig.xaxis.axis_label = 'Pixel Column Number'

    vlo, lo, hi, vhi = np.nanpercentile(tpf.flux - pedestal, [0.2, 1, 95, 99.8])
    vstep = (np.log10(vhi) - np.log10(vlo)) / 300.0  # assumes counts >> 1.0!
    color_mapper = LogColorMapper(palette="Viridis256", low=lo, high=hi)

    fig.image([tpf.flux[fiducial_frame, :, :] - pedestal], x=tpf.column, y=tpf.row,
              dw=tpf.shape[2], dh=tpf.shape[1], dilate=True,
              color_mapper=color_mapper, name="tpfimg")

    color_bar = ColorBar(color_mapper=color_mapper,
                         ticker=LogTicker(desired_num_ticks=8),
                         label_standoff=-10, border_line_color=None,
                         location=(0, 0), background_fill_color='whitesmoke',
                         major_label_text_align='left',
                         major_label_text_baseline='middle',
                         title='e/s', margin=0)
    fig.add_layout(color_bar, 'right')

    color_bar.formatter = PrintfTickFormatter(format="%14u")

    if tpf_source is not None:
        fig.rect('xx', 'yy', 1, 1, source=tpf_source, fill_color='gray', fill_alpha=0.4, line_color='white')

    return fig
