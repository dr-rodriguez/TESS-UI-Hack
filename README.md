# TESS UI Hack

Python in Astronomy 2019 hack day project for a TESS UI.

Utilizes [AladinLite](https://aladin.u-strasbg.fr/AladinLite/) for the main display, 
[TESScut](https://mast.stsci.edu/tesscut/) to generate cutouts, 
[lightkurve](https://github.com/KeplerGO/lightkurve) to handle the target pixel files, and 
[Bokeh](https://bokeh.pydata.org/en/latest/) to generate some of the plots.

TESS HiPS files were generated using median-stacked FFI images and with the script [here](https://github.com/dr-rodriguez/TESS-HiPS).

A small demo is available at [http://tess-ui-hack19.herokuapp.com/](http://tess-ui-hack19.herokuapp.com/)
