# -*- coding: UTF-8 -*-

import unittest2
import re
import os
from datetime import date, timedelta

from pedidos.model.order_product import OrderProduct, OrderProductDAO
from pedidos.test.support.testcase import DatabseBackedTestCase

class TestOrderProduct(DatabseBackedTestCase):
    def setUp(self):
        self.dao = OrderProductDAO()
        super(self.__class__, self).setUp()

    def test_attrs_have_a_default_value(self):
        order_product = OrderProduct()
        self.assertEqual(0, order_product.id)
        self.assertEqual(date.today(), order_product.ordered_on)
        self.assertEqual(order_product.name, "")
        self.assertEqual(order_product.quantity, 1)
        self.assertEqual(order_product.isurgent, False)
        self.assertEqual(order_product.isordered, False)

    def test_name_cant_be_blank(self):
        order_product = OrderProduct()
        self.assertFalse(order_product.isvalid())
        self.assertIn("no puede estar en blanco", order_product.errors.on("name"))

    def test_ordered_on_is_not_earlier_than_today(self):
        today = date.today()        
        yesterday = date.today() + timedelta(days=-1)
        order_product = OrderProduct(name="Amoxidal", ordered_on=yesterday)
        self.assertFalse(order_product.isvalid())
        self.assertIn("debe ser igual o posterior a la fecha actual", order_product.errors.on("ordered_on"))
        order_product = OrderProduct(name="Amoxidal", ordered_on=today)
        self.assertTrue(order_product.isvalid())

    def test_name_must_be_unique_on_any_given_date(self):
        product1 = OrderProduct(name="Amoxidal")
        product2 = OrderProduct(name="Amoxidal")
        self.assertTrue(product1.isvalid())
        product1.save()
        self.assertFalse(product2.isvalid())
        self.assertIn("ya ha sido pedido en esa fecha", product2.errors.on("name"))

    def test_save(self):
        order_product = OrderProduct(name="Amoxidal")
        self.assertTrue(order_product.save())
        self.assertGreater(order_product.id, 0)

        order_product.name += " Duo"
        order_product.isordered = True
        self.assertTrue(order_product.save())
        self.assertEqual("Amoxidal Duo", order_product.name)

    def test_eq(self):
        prod1, prod2 = OrderProduct(id=1), OrderProduct(id=2)
        self.assertNotEqual(prod1, prod2)
        prod2 = OrderProduct(id=1)
        self.assertEqual(prod1, prod2)

    def test_isnewrecord(self):    
        order_product = OrderProduct(name="Amoxidal")
        self.assertTrue(order_product.isnewrecord())
        order_product.save()        
        self.assertFalse(order_product.isnewrecord())

    def test_find_by_ordered_on_and_name(self):
        product = OrderProduct(name="Amoxidal")
        product.save()
        order_product = OrderProduct.find_by_ordered_on_and_name(product.ordered_on, product.name)
        self.assertEqual(product, order_product)

    def test_find_all_by_ordered_on(self):
        amoxidal = OrderProduct(name="Amoxidal")
        amoxidal.save()
        sertal = OrderProduct(name="Sertal")
        sertal.save()
        order_products = OrderProduct.find_all_by_ordered_on(date.today())
        self.assertEqual(2, len(order_products))
        self.assertEqual(amoxidal, order_products[0])
        self.assertEqual(sertal, order_products[1])

    def test_deletes_a_single_instance(self):
        amoxidal = OrderProduct(name="Amoxidal")
        amoxidal.save()
        self.assertEqual(1, amoxidal.delete())
        order_products = OrderProduct.find_all_by_ordered_on(amoxidal.ordered_on)
        self.assertEqual([], order_products)

    def test_find_all_not_ordered_before(self):
        amoxidal = OrderProduct(name="Amoxidal")
        amoxidal.save()
        sertal = OrderProduct(name="Sertal", isordered=True)
        sertal.save()
        tomorrow = date.today() + timedelta(days=1)
        order_products = OrderProduct.find_all_not_ordered_before(tomorrow)
        self.assertEqual([amoxidal], order_products)

    def test_reorder_pending_products(self):
        self.assertIsNone(OrderProduct.reorder_pending_products())
        yesterday = date.today() - timedelta(days=1)
        amoxidal = OrderProduct(name="Amoxidal", ordered_on=yesterday)
        self.assertTrue(amoxidal.save(validate=False))
        self.assertEqual(1, OrderProduct.reorder_pending_products())

    def test_find_all_unique_names_ordered_last_month(self):
        today = date.today()
        a_week_ago = today - timedelta(weeks=1)
        two_weeks_ago = today - timedelta(weeks=2)
        a_month_ago = today - timedelta(weeks=4)

        OrderProduct(name="Amoxidal", ordered_on=a_week_ago).save(False)
        OrderProduct(name="amoxidal", ordered_on=two_weeks_ago).save(False)
        OrderProduct(name="Sertal", ordered_on=two_weeks_ago).save(False)
        OrderProduct(name="sertal", ordered_on=a_week_ago).save(False)

        unique_names = OrderProduct.find_all_unique_names_ordered_last_month()
        self.assertEqual(2, len(unique_names))
    
        amoxidalre = re.compile(r'amoxidal', re.IGNORECASE)
        sertalre = re.compile(r'sertal', re.IGNORECASE)
        for regex in (amoxidalre, sertalre):
            matched = filter(lambda name: re.match(regex, name), unique_names)
            self.assertEqual(1, len(matched))
            
    def test_find_all_not_yet_ordered_on(self):
        amoxidal = OrderProduct(name="Amoxidal")
        amoxidal.save()
        OrderProduct(name="Sertal", isordered=True).save()
        order_products = OrderProduct.find_all_not_yet_ordered_on(date.today())
        self.assertEqual([amoxidal], order_products)


class TestOrderProductDAO(DatabseBackedTestCase):
    def setUp(self):
        self.dao = OrderProductDAO()
        super(self.__class__, self).setUp()

    def test_save(self):
        order_product = OrderProduct(name="Amoxidal")
        order_product.id = self.dao.save(order_product)
        self.assertGreater(order_product.id, 0)

        order_product.name += " Duo"
        self.assertGreater(order_product.save(), 0)
        self.assertEqual("Amoxidal Duo", order_product.name)

    def test_mass_update_ordered_on(self):
        today = date.today()        
        tomorrow = today + timedelta(days=1)
        amoxidal = OrderProduct(name="Amoxidal", ordered_on=tomorrow)
        amoxidal.save()
        sertal = OrderProduct(name="Sertal", ordered_on=tomorrow)
        sertal.save()
        affected_rows = self.dao.mass_update_ordered_on(today, (amoxidal.id, sertal.id))
        self.assertEqual(2, affected_rows)

    def test_find_all_unique_names_ordered_between(self):
        today = date.today()
        a_week_from_today = today + timedelta(weeks=1)
        two_weeks_from_today = today + timedelta(weeks=2)
        a_month_from_today = today + timedelta(weeks=4)

        OrderProduct(name="Amoxidal", ordered_on=a_week_from_today).save()
        OrderProduct(name="amoxidal", ordered_on=two_weeks_from_today).save()
        OrderProduct(name="Sertal", ordered_on=two_weeks_from_today).save()
        OrderProduct(name="sertal", ordered_on=a_week_from_today).save()
        
        unique_names = self.dao.find_all_unique_names_ordered_between(today, a_month_from_today)
        self.assertEqual(2, len(unique_names))
    
        amoxidalre = re.compile(r'amoxidal', re.IGNORECASE)
        sertalre = re.compile(r'sertal', re.IGNORECASE)
        for regex in (amoxidalre, sertalre):
            matched = filter(lambda name: re.match(regex, name), unique_names)
            self.assertEqual(1, len(matched))
