#! /usr/bin/env python

import warnings
from glob import glob
try:
    from setuptools import setup
    SETUPTOOLS_PRESENT = True
except:
    from distutils.core import setup
    SETUPTOOLS_PRESENT = False

if SETUPTOOLS_PRESENT:
    extras = {"entry_points": {
        'console_scripts': [
            'plot2table = plottotable:main'
        ]
    }}
else:
    extras = {}
    warnings.warn(
        "CLI tool would not work without the setuptools module. "
        "Use launch.py script to start the software."
    )


if __name__ == "__main__":
    setup(
        name="PlotToTable",
        packages=['plottotable', 'plottotable.tests'],
        scripts=['bin/multicrop'],
        data_files = [
            ('plottotable/data/', glob('plottotable/data/*')),
            ('plottotable/test-inputs/', glob('plottotable/test-inputs/*')),
            ('plottotable/user-manual/', glob('plottotable/user-manual/*'))
            ],
        **extras
    )
