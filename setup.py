from distutils.core import setup
from glob import glob
import py2exe

setup(
    windows = [
        {
            'script': 'autoprint.py',
            'icon_resources': [(1, 'printer.ico')]
        }
    ],
    options = {
        "py2exe" : {
            "includes" : ['sys', 'PySide', 'PySide.QtNetwork']
        }
    }
)
