"""
Script for building the example.

Usage:
    python setup.py py2app
"""
from distutils.core import setup
import py2app

NAME = 'Replay'
VERSION = '2.0'

plist = dict(
    CFBundleIconFile=NAME,
    CFBundleName=NAME,
    CFBundleShortVersionString=VERSION,
    CFBundleGetInfoString=' '.join([NAME, VERSION]),
    CFBundleExecutable=NAME,
    CFBundleIdentifier='org.cmu.PSF',
    LSArchitecturePriority='i386'
)

setup(
    data_files=['gfx', 'fonts', 'sounds'],
    options={'py2app': {'iconfile': 'PSF.icns', 'arch': 'i386'}},
    app=[
        dict(script="replay.py", plist=plist),
    ],
)
