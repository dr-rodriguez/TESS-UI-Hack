from flask import Flask, render_template, request, redirect, make_response
# from bokeh.plotting import figure
# from bokeh.embed import components
# from bokeh.models import ColumnDataSource, HoverTool, OpenURL, TapTool
# import numpy as np
# from astropy.io import fits
# from astropy.utils.data import download_file
# from astropy.wcs import WCS
# from bokeh.palettes import Spectral4
# from astroquery.mast import Catalogs, Observations
# from bokeh.models import DataTable, TableColumn
# from bokeh.layouts import column, widgetbox
from lightkurve.search import search_tesscut
from .utils import interact_widget, simple_ui

app_portal = Flask(__name__)


# Redirect to the main page
@app_portal.route('/')
@app_portal.route('/index')
@app_portal.route('/index.html')
def app_home():
    return render_template('index.html')


@app_portal.route('/test')
def get_cut():
    s = search_tesscut(target='TW Hya', sector=9)
    tpf = s.download()
    script, div = simple_ui(tpf)
    return render_template('lightcurve.html', script=script, div=div)


@app_portal.route('/get_data', methods=['GET'])
def get_data():
    ra = request.args.get('ra')
    dec = request.args.get('dec')
    msg = 'I have received {} and {}'.format(ra, dec)
    print(msg)

    # Get the data
    s = search_tesscut(target='{} {}'.format(ra, dec), sector=1)
    tpf = s.download()
    script, div = simple_ui(tpf)

    output_text = 'Lightcurve generated for coordinates: {} {}'.format(ra, dec)

    return render_template('lightcurve.html', output_text=output_text, script=script, div=div)
