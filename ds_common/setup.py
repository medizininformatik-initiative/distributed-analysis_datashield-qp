#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:copyright: (c) 2018 by Sido Haakma
:license: GNU, see LICENSE for more details.
"""
import os
import sys

from setuptools import setup

setup(name='ds_common',
      version='0.0.3',
      description='Common services for DataSHIELD Poll-Qua mechanism',
      url='https://github.com/juliangruendner/ds_common',
      author='Julian Gruendner',
      author_email='julian.gruendner@fau.de ',
      license='GNU',
      packages=['ds_http'],
      zip_safe=False)