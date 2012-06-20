# -*- coding: UTF-8 -*-

import unittest2
import os

class DatabseBackedTestCase(unittest2.TestCase):
  # @classmethod
  # def tearDownClass(cls):
  #   try:
  #     del cls.dao
  #   except AttributeError: pass
  
    def setUp(self):
        os.environ["PY_ENV"] = "test"

    def tearDown(self):
        self.dao.tearDown()
