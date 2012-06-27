# -*- coding: UTF-8 -*-

import unittest2

from pedidos.ui.text_printer import OrderProductPrinter
from pedidos.model.order_product import OrderProduct

class TestOrderProductPrinter(unittest2.TestCase):
    def setUp(self):
        order_products = []
        for i in xrange(1, OrderProductPrinter.ORDER_PRODUCTS_PER_PAGE+20):
            order_products.append(OrderProduct(quantity=i, name="Product #%d" % i))
        
        self.printer = OrderProductPrinter(order_products)
        
    def test_calc_n_pages(self):
        self.assertEqual(2, self.printer.calc_n_pages())
        
    def test_print_page(self):
        page1 = self.printer.print_page(0)
        self.assertRegexpMatches(page1, r"Product #%d" % OrderProductPrinter.ORDER_PRODUCTS_PER_PAGE)
        page2 = self.printer.print_page(1)
        self.assertRegexpMatches(page2, r"Product #%d" % (OrderProductPrinter.ORDER_PRODUCTS_PER_PAGE+1))