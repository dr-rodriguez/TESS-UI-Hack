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

app_portal = Flask(__name__)

# Redirect to the main page
@app_portal.route('/')
@app_portal.route('/index')
@app_portal.route('/index.html')
def app_home():
    return render_template('index.html')
