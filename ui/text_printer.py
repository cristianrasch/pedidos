from __future__ import division
import math

class OrderProductPrinter(object):
    ORDER_PRODUCTS_PER_PAGE = 55
    
    def __init__(self, order_products):
        self.order_products = order_products
    
    def print_page(self, page_nr):
        products_list = ["Cantidad\tProducto\n"]
        page_scoped_products = self.order_products[page_nr*self.ORDER_PRODUCTS_PER_PAGE:(page_nr+1)*self.ORDER_PRODUCTS_PER_PAGE]
        products_list.extend(map(lambda order_product: "(%d)\t\t%s" % (order_product.quantity, order_product.name), page_scoped_products))
        return "\n".join(products_list)
    
    def calc_n_pages(self):
        return int(math.ceil(len(self.order_products)/self.ORDER_PRODUCTS_PER_PAGE))
