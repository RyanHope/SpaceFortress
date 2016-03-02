"""
Script for building the example.

Usage:
    python setup.py py2app
"""
from distutils.core import setup
import py2app

NAME = 'PSF'
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
    data_files=['gfx', 'fonts', 'sounds', 'gui-theme'],
    options={'py2app': {'excludes': 'OpenGL', 'iconfile': 'PSF.icns', 'arch': 'i386'}},
    app=[
        dict(script="allinone_main.py", plist=plist),
    ],
)
