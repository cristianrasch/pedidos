# -*- coding: UTF-8 -*-

import gtk
import os

from random import randint
from datetime import date

curr_dir = os.path.dirname(__file__)
def relative_path(path):
    return os.path.join(curr_dir, *path.split("/"))


class App(object):
    def __init__(self):
        self.build_from_glade_xml()
        self.reset_calendar()
        self.reset_product_quantity()
        self.build_product_view()
        
    def build_from_glade_xml(self):
        self.builder = gtk.Builder()
        glade_xml = relative_path("ui.glade")
        self.builder.add_from_file(glade_xml)
        self.builder.connect_signals(self)

        self.calendar = self.builder.get_object("calendar")
        self.name = self.builder.get_object("name")
        self.quantity = self.builder.get_object("quantity")
        self.urgency = self.builder.get_object("urgency")
        self.title = self.builder.get_object("title")
        
    def reset_product_quantity(self):
        self.quantity.set_value(1)
      
    def build_product_view(self):
        window = self.builder.get_object("scrolledwindow")
        self.product_model = ProductModel()        
        self.product_view = ProductView(self.product_model)        
        self.product_view.connect("cursor-changed", self.on_product_clicked)
        self.product_view.connect("select-cursor-row", self.on_product_double_clicked)
        window.add(self.product_view)
        window.show_all()

    def reset_calendar(self):
        today = date.today()
        self.calendar.select_month(today.month-1, today.year)
        self.calendar.select_day(today.day)
        
    def run(self):
        self.builder.get_object("window").show()
        gtk.main()
    
    def on_window_delete_event(self, widget, data=None):
        gtk.main_quit()
        return False

    def on_save_clicked(self, widget):
        model, treeiter = self.product_view.get_selected()
        urgency = ProductModel.STAR_ICON if self.urgency.get_active() else None
        name = self.name.get_text()
        quantity = self.quantity.get_value()

        if treeiter:
            model.set_value(treeiter, ProductModel.URGENCY_IDX, urgency)
            model.set_value(treeiter, ProductModel.NAME_IDX, name)
            model.set_value(treeiter, ProductModel.QUANTITY_IDX, quantity)
        else:
            model.append([0, urgency, name, quantity, False])
        
        self.reset_form()

    def on_clear_clicked(self, widget):
        self.reset_calendar()
        self.reset_form()

    def reset_form(self):
        self.name.set_text("")
        self.reset_product_quantity()
        self.urgency.set_active(False)
        
    def on_calendar_day_selected(self, widget):
        year, month, day = widget.get_date()
        selected_date = date(year, month+1, day)
        self.title.set_text("Pedido del %s" % selected_date.strftime("%d/%m"))
        if hasattr(self, "product_model"):
            self.product_model.rebuild(selected_date.day)

    def on_product_clicked(self, treeview):
        treeiter = treeview.get_selected()[1]
        if not treeiter: return
        model = treeview.get_model()
        urgency, name, quantity, ordered = model.get(treeiter, *range(1, 5))
        if not ordered:        
            self.urgency.set_active(urgency is not None)
            self.name.set_text(name)
            self.quantity.set_value(quantity)

    def on_product_double_clicked(self, treeview, start_editing):
        treeiter, model = treeview.get_selected()[1], treeview.get_model()
        model.remove(treeiter)

class ProductModel(gtk.ListStore):
    STAR_ICON = gtk.gdk.pixbuf_new_from_file(relative_path("images/star.png"))
    ID_IDX = 0
    URGENCY_IDX = 1
    NAME_IDX = 2
    QUANTITY_IDX = 3
    ORDERED_IDX = 4

    def __init__(self):
        super(ProductModel, self).__init__(int, gtk.gdk.Pixbuf, str, int, "gboolean")
        howmany = randint(1, 10)
        self.append_products(howmany)
      
    def rebuild(self, howmany):
        self.clear()
        self.append_products(howmany)

    def append_products(self, howmany):
        for i in xrange(howmany):
            icon = self.STAR_ICON if (i%2)!=0 else None
            product_name = "Producto #%d" % (i+1)
            self.append([i+1, icon, product_name, randint(1, i+1), (i%2)==0])

class ProductView(gtk.TreeView):
    def __init__(self, model):
        super(ProductView, self).__init__(model)
        pixbuf_renderer = gtk.CellRendererPixbuf()
        text_renderer = gtk.CellRendererText()
        toggle_renderer = gtk.CellRendererToggle()
        toggle_renderer.set_property("activatable", True)
        toggle_renderer.connect("toggled", self.on_product_ordered_toggled, model)
        product_urgency_column = gtk.TreeViewColumn("Urgente?", pixbuf_renderer, pixbuf=ProductModel.URGENCY_IDX)
        self.append_column(product_urgency_column)
        product_name_column = gtk.TreeViewColumn("Producto", text_renderer, text=ProductModel.NAME_IDX)
        self.append_column(product_name_column)
        product_quantity_column = gtk.TreeViewColumn("Cantidad", text_renderer, text=ProductModel.QUANTITY_IDX)
        self.append_column(product_quantity_column)
        product_ordered_column = gtk.TreeViewColumn("Pedido?", toggle_renderer)
        product_ordered_column.add_attribute(toggle_renderer, "active", ProductModel.ORDERED_IDX)
        self.append_column(product_ordered_column)

    def on_product_ordered_toggled(self, cell, path, model):
        model[path][ProductModel.ORDERED_IDX] = not model[path][ProductModel.ORDERED_IDX]

    def get_selected(self):
        return self.get_selection().get_selected()

