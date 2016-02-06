"""
Script for building the example.

Usage:
    python setup.py py2app
"""
from distutils.core import setup
import py2app

NAME = 'ModelServer'
VERSION = '1.0'

plist = dict(
    CFBundleIconFile=NAME,
    CFBundleName=NAME,
    CFBundleShortVersionString=VERSION,
    CFBundleGetInfoString=' '.join([NAME, VERSION]),
    CFBundleExecutable=NAME,
    CFBundleIdentifier='org.cmu.anderson.'+NAME,
)

setup(
    data_files=['gfx', 'fonts', 'sounds'],
    options={'py2app': {}},
    app=[
        dict(script="wx_model_main.py", plist=plist),
    ],
)
