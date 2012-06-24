# -*- coding: UTF-8 -*-

import unittest2
import re

from pedidos.model.base import Model, Errors

class TestModel(unittest2.TestCase):
    def test_isvalid(self):
        model = Model()        
        self.assertTrue(model.isvalid())
        model.errors.add("attr", "err")
        self.assertFalse(model.isvalid())

    def test_save(self):
        self.assertTrue(Model().save())

    def test_sets_attr_values(self):
        model = Model(firstname="Homer", lastname="Simpson")
        self.assertEqual(model.firstname, "Homer")
        self.assertEqual(model.lastname, "Simpson")

    def test_reports_an_attrs_name(self):
        self.assertEquals(Model().attr_name("attr1"), "attr1")


class TestErrors(unittest2.TestCase):
    def setUp(self):
        self.err = Errors(Model())

    def test_isempty(self):
        self.assertTrue(self.err.isempty())

    def test_adds_errors(self):
        self.err.add("attr", "err")
        self.assertFalse(self.err.isempty())

    def test_reports_errors_on_attr(self):
        self.err.add("attr", "err")
        self.assertEqual(self.err.on("attr"), ["err"])

    def test_reports_full_error_messages(self):
        self.err.add("attr1", "err1")
        self.err.add("attr1", "err2")
        self.err.add("attr2", "err1")
        errors = self.err.fullmessages()
        self.assertIsNotNone(re.search(r"attr1 err1, err2", errors))
        self.assertIsNotNone(re.search(r"attr2 err1", errors))
