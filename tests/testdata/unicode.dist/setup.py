# coding: utf-8
from setuptools import setup

# Only run this test if we are on Python3 or not on Windows
import os
import platform
import sys

if platform.platform != "Windows" or sys.version_info[0] > 2:
    os.replace('./unicodedist/_rename_to_unicode_.py','./unicodedist/åäö_日本語.py')
    setup(name='unicode.dist',
        version='0.1',
        description=u'A testing distribution \N{SNOWMAN}',
        packages=['unicodedist']
        )
