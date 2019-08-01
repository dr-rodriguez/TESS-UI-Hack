# Modifications to lightkurve interact
# CAN'T USE CALLBACKS IN PYTHON UNLESS SERVER OR NOTEBOOK

import numpy as np
# from bokeh.io import show, output_notebook, push_notebook, output_file
from bokeh.plotting import figure, ColumnDataSource
from bokeh.models import LogColorMapper, Selection, Slider, RangeSlider, \
    Span, ColorBar, LogTicker, Range1d
from bokeh.layouts import layout, Spacer
from bokeh.models.tools import HoverTool
from bokeh.models.widgets import Button, Div
from bokeh.models.formatters import PrintfTickFormatter
from bokeh.embed import components
from lightkurve.interact import prepare_lightcurve_datasource, prepare_tpf_datasource, \
    make_lightcurve_figure_elements, make_tpf_figure_elements, get_lightcurve_y_limits


def simple_ui(tpf):
    # aperture_mask = tpf._parse_aperture_mask('pipeline')
    ap_mask = tpf.create_threshold_mask()
    lc = tpf.to_lightcurve(aperture_mask=ap_mask)
    lc_source = prepare_lightcurve_datasource(lc)
    # tpf_source = prepare_tpf_datasource(tpf, aperture_mask)

    title = "Lightcurve for {} (TESS Sec. {})".format(lc.label, lc.sector)

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

    script, div = components(fig)

    return script, div

def interact_widget(tpf, max_cadences=30000,
                         aperture_mask='pipeline'):

    aperture_mask = tpf._parse_aperture_mask(aperture_mask)

    lc = tpf.to_lightcurve(aperture_mask=aperture_mask)

    npix = tpf.flux[0, :, :].size
    pixel_index_array = np.arange(0, npix, 1).reshape(tpf.flux[0].shape)

    # Bokeh cannot handle many data points
    # https://github.com/bokeh/bokeh/issues/7490
    if len(lc.cadenceno) > max_cadences:
        msg = 'Interact cannot display more than {} cadences.'
        raise RuntimeError(msg.format(max_cadences))

    def create_interact_ui():
        # The data source includes metadata for hover-over tooltips
        lc_source = prepare_lightcurve_datasource(lc)
        tpf_source = prepare_tpf_datasource(tpf, aperture_mask)

        # Create the lightcurve figure and its vertical marker
        fig_lc, vertical_line = make_lightcurve_figure_elements(lc, lc_source)

        # Create the TPF figure and its stretch slider
        pedestal = np.nanmin(tpf.flux)
        fig_tpf, stretch_slider = make_tpf_figure_elements(tpf, tpf_source,
                                                           pedestal=pedestal,
                                                           fiducial_frame=0)

        # Helper lookup table which maps cadence number onto flux array index.
        tpf_index_lookup = {cad: idx for idx, cad in enumerate(tpf.cadenceno)}

        # Interactive slider widgets and buttons to select the cadence number
        cadence_slider = Slider(start=np.min(tpf.cadenceno),
                                end=np.max(tpf.cadenceno),
                                value=np.min(tpf.cadenceno),
                                step=1,
                                title="Cadence Number",
                                width=490)
        r_button = Button(label=">", button_type="default", width=30)
        l_button = Button(label="<", button_type="default", width=30)
        export_button = Button(label="Save Lightcurve",
                               button_type="success", width=120)
        message_on_save = Div(text=' ',width=600, height=15)

        # Callbacks
        def update_upon_pixel_selection(attr, old, new):
            """Callback to take action when pixels are selected."""
            # Check if a selection was "re-clicked", then de-select
            if ((sorted(old) == sorted(new)) & (new != [])):
                # Trigger recursion
                tpf_source.selected.indices = new[1:]

            if new != []:
                selected_indices = np.array(new)
                selected_mask = np.isin(pixel_index_array, selected_indices)
                lc_new = tpf.to_lightcurve(aperture_mask=selected_mask)
                lc_source.data['flux'] = lc_new.flux
                ylims = get_lightcurve_y_limits(lc_source)
                fig_lc.y_range.start = ylims[0]
                fig_lc.y_range.end = ylims[1]
            else:
                lc_source.data['flux'] = lc.flux * 0.0
                fig_lc.y_range.start = -1
                fig_lc.y_range.end = 1

            message_on_save.text = " "
            export_button.button_type = "success"

        def update_upon_cadence_change(attr, old, new):
            """Callback to take action when cadence slider changes"""
            if new in tpf.cadenceno:
                frameno = tpf_index_lookup[new]
                fig_tpf.select('tpfimg')[0].data_source.data['image'] = \
                    [tpf.flux[frameno, :, :] - pedestal]
                vertical_line.update(location=tpf.time[frameno])
            else:
                fig_tpf.select('tpfimg')[0].data_source.data['image'] = \
                    [tpf.flux[0, :, :] * np.NaN]
            lc_source.selected.indices = []

        def go_right_by_one():
            """Step forward in time by a single cadence"""
            existing_value = cadence_slider.value
            if existing_value < np.max(tpf.cadenceno):
                cadence_slider.value = existing_value + 1

        def go_left_by_one():
            """Step back in time by a single cadence"""
            existing_value = cadence_slider.value
            if existing_value > np.min(tpf.cadenceno):
                cadence_slider.value = existing_value - 1

        def jump_to_lightcurve_position(attr, old, new):
            if new != []:
                cadence_slider.value = lc.cadenceno[new[0]]

        # Map changes to callbacks
        r_button.on_click(go_right_by_one)
        l_button.on_click(go_left_by_one)
        tpf_source.selected.on_change('indices', update_upon_pixel_selection)
        lc_source.selected.on_change('indices', jump_to_lightcurve_position)
        # export_button.on_click(save_lightcurve)
        cadence_slider.on_change('value', update_upon_cadence_change)

        # Layout all of the plots
        sp1, sp2, sp3 = (Spacer(width=15), Spacer(width=30), Spacer(width=80))
        widgets_and_figures = layout([fig_lc, fig_tpf],
                                     [l_button, sp1, r_button, sp2,
                                     cadence_slider, sp3, stretch_slider])
        return widgets_and_figures
        # doc.add_root(widgets_and_figures)

    # output_notebook(verbose=False, hide_banner=True)
    # output_file()

    script, div = components(create_interact_ui)

    # return show(create_interact_ui, notebook_url=notebook_url)
    return script, div
