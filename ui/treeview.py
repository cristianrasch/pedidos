# -*- coding: UTF-8 -*-

import gtk
import gobject

from datetime import date
from random import randint

from pedidos.helpers import relative_path
from pedidos.model.order_product import OrderProduct

class ProductModel(gtk.ListStore):
    STAR_ICON = gtk.gdk.pixbuf_new_from_file(relative_path("ui/images/star.png"))
    PROD_IDX = 0
    URGENCY_IDX = 1
    NAME_IDX = 2
    QUANTITY_IDX = 3
    ORDERED_IDX = 4

    def __init__(self):
        super(ProductModel, self).__init__(gobject.TYPE_PYOBJECT, gtk.gdk.Pixbuf, 
                                           str, int, "gboolean")

        self._selected_date = date.today()

    @property
    def selected_date(self):
        return self._selected_date    

    @selected_date.setter
    def selected_date(self, value):
        self._selected_date = value
        self.clear()
        for order_product in OrderProduct.find_all_by_ordered_on(value):
            self.append_order_product(order_product)

    def append_order_product(self, order_product):
        l = []
        l.append(order_product)
        l.append(self.urgency_icon(order_product))
        l.append(order_product.name)
        l.append(order_product.quantity)
        l.append(order_product.isordered)
        self.append(l)

    def update_order_product(self, treeiter, order_product):
        self.set_value(treeiter, ProductModel.URGENCY_IDX, self.urgency_icon(order_product))
        self.set_value(treeiter, ProductModel.NAME_IDX, order_product.name)
        self.set_value(treeiter, ProductModel.QUANTITY_IDX, order_product.quantity)
        self.set_value(treeiter, ProductModel.ORDERED_IDX, order_product.isordered)

    def urgency_icon(self, order_product):
        return self.STAR_ICON if order_product.isurgent else None


class ProductView(gtk.TreeView):
    def __init__(self, model):
        super(ProductView, self).__init__(model)
        pixbuf_renderer = gtk.CellRendererPixbuf()
        text_renderer = gtk.CellRendererText()
        right_aligned_text_renderer = gtk.CellRendererText()
        right_aligned_text_renderer.set_alignment(1.0, 0.5)
        toggle_renderer = gtk.CellRendererToggle()
        toggle_renderer.set_property("activatable", True)
        toggle_renderer.connect("toggled", self.on_product_ordered_toggled)
        
        product_urgency_column = gtk.TreeViewColumn("Urgente?", pixbuf_renderer, 
                                                    pixbuf=model.URGENCY_IDX)
        self.configure_and_add_column(product_urgency_column)
        product_urgency_column.set_expand(False)
        
        product_name_column = gtk.TreeViewColumn("Producto", text_renderer, 
                                                 text=model.NAME_IDX)
        self.configure_and_add_column(product_name_column)
        product_name_column.set_expand(True)
        
        product_quantity_column = gtk.TreeViewColumn("Cantidad", 
                                                     right_aligned_text_renderer, 
                                                     text=model.QUANTITY_IDX)
        self.configure_and_add_column(product_quantity_column)
        product_quantity_column.set_expand(False)
        
        product_ordered_column = gtk.TreeViewColumn("Pedido?", toggle_renderer)
        self.configure_and_add_column(product_ordered_column)
        product_ordered_column.set_expand(False)
        product_ordered_column.add_attribute(toggle_renderer, "active", model.ORDERED_IDX)

    def on_product_ordered_toggled(self, cell, path):
        model = self.get_model()
        order_product = model[path][model.PROD_IDX]
        if order_product.ordered_on >= date.today():
            order_product.toggle_isordered()
            order_product.save()
            model[path][model.ORDERED_IDX] = order_product.isordered

    def get_selected(self):
        return self.get_selection().get_selected()

    def configure_and_add_column(self, column):
        column.set_resizable(True)
        column.set_alignment(0.5)
        self.append_column(column)
