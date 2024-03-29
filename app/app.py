from flask import Flask, render_template, request
from lightkurve.search import search_tesscut
from lightkurve.targetpixelfile import TessTargetPixelFile
from .utils import simple_ui

app_portal = Flask(__name__)


# Redirect to the main page
@app_portal.route('/')
@app_portal.route('/index')
@app_portal.route('/index.html')
def app_home():
    return render_template('index.html')


@app_portal.route('/test')
def get_cut():
    tpf = TessTargetPixelFile('app/static/astrocut_165.47079_-34.70688_10x10px.zip')
    script, div = simple_ui(tpf)
    return render_template('lightcurve.html', output_text='Example (TW Hya)', script=script, div=div)


@app_portal.route('/get_data', methods=['GET'])
def get_data():
    ra = request.args.get('ra')
    dec = request.args.get('dec')
    msg = 'I have received {} and {}'.format(ra, dec)
    print(msg)

    # Get the data
    try:
        s = search_tesscut(target='{} {}'.format(ra, dec))
        tpf = s[0].download()
        ap_mask = tpf.create_threshold_mask()
        num_sectors = len(s)
    except Exception as e:
        try:
            num_sectors = len(s)
        except:
            num_sectors = 0

        msg = 'Data found for {} sectors.<br>Could not download data for {} {}.<br>Error: {}'.format(num_sectors, ra, dec, e)
        print(msg)
        return render_template('error.html', output_text=msg)

    script, div = simple_ui(tpf, ap_mask)

    output_text = 'Data found for {} sectors.<br>TESS data for coordinates: {} {}'.format(num_sectors, ra, dec)
    if ap_mask.sum() == 0:
        output_text += '<br>Warning: encountered issue determining pixels to use for lightcurve.'

    return render_template('lightcurve.html', output_text=output_text,
                           script=script, div=div)

