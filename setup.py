"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup

NAME = 'psf'
VERSION = '1.4'
APP = ['PSF.py']
DATA_FILES = ['gfx', 'sounds', 'fonts']
OPTIONS = {'iconfile': 'psf.icns', 'argv_emulation': True}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
