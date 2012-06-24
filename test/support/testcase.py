# -*- coding: UTF-8 -*-

import unittest2
import os

class DatabseBackedTestCase(unittest2.TestCase):
    def setUp(self):
        os.environ["PY_ENV"] = "test"

    def tearDown(self):
        self.dao.tearDown()
