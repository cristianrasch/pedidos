#!/usr/bin/env python

# -*- coding: UTF-8 -*-

import os
import sys

def expandpath():
  realpath = os.path.realpath(__file__)
  currdir = os.path.dirname(realpath)
  rootdir = os.path.join(currdir, os.path.pardir)
  sys.path.insert(0, os.path.normpath(rootdir))
expandpath()

from pedidos.ui.app import App

if __name__ == "__main__":
    app = App()
    app.run()
