import os
from distutils.core import setup
import py2exe
from glob import glob

setup(windows = ['prog.py'],
      data_files=["config.txt", "przerwy.txt", "license.txt", "gdiplus.dll", "MSVCP90.dll"],
      name='Odtwarzacz',
      version='1.0',
      description='Music player, which turns on and off the music at specified time.',
      author='Szymon Zmilczak',
      zipfile="data.lib",
      options = {"py2exe": {"compressed": 3, 
                            "optimize": 2,
                            "bundle_files": 3
                         }
              }
      #packages=['distutils', 'distutils.command', 'wx'],
      )

