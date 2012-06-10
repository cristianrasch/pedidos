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
        product_view = ProductView(self.product_model)        
        product_view.connect("cursor-changed", self.on_product_selected, self.product_model)
        window.add(product_view)
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

    def on_clear_clicked(self, widget):
        self.reset_calendar()
        self.name.set_text("")
        self.reset_product_quantity()
        self.urgency.set_active(False)
        
    def on_calendar_day_selected(self, widget):
        year, month, day = widget.get_date()
        selected_date = date(year, month+1, day)
        self.title.set_text("Pedido del %s" % selected_date.strftime("%d/%m"))
        if hasattr(self, "product_model"):
            self.product_model.rebuild(selected_date.day)

    def on_product_selected(self, treeview, model):
        treeiter = treeview.get_selection().get_selected()[1]
        urgency, name, quantity, ordered = model.get(treeiter, *range(4))
        if not ordered:        
            self.builder.get_object("urgency").set_active(urgency is not None)
            self.builder.get_object("name").set_text(name)
            self.quantity.set_value(quantity)

class ProductModel(gtk.ListStore):
    def __init__(self):
        super(ProductModel, self).__init__(gtk.gdk.Pixbuf, str, int, "gboolean")
        icon_path = relative_path("images/star.png")
        self.star_icon = gtk.gdk.pixbuf_new_from_file(icon_path)
        howmany = randint(1, 10)
        self.append_products(howmany)
      
    def rebuild(self, howmany):
        self.clear()
        self.append_products(howmany)

    def append_products(self, howmany):
        for i in xrange(howmany):
            icon = self.star_icon if (i%2)!=0 else None
            product_name = "Producto #%d" % (i+1)
            self.append([icon, product_name, randint(1, i+1), (i%2)==0])

class ProductView(gtk.TreeView):
    def __init__(self, model):
        super(ProductView, self).__init__(model)
        pixbuf_renderer = gtk.CellRendererPixbuf()
        text_renderer = gtk.CellRendererText()
        toggle_renderer = gtk.CellRendererToggle()
        toggle_renderer.set_property("activatable", True)
        toggle_renderer.connect("toggled", self.on_product_ordered_toggled, model)
        product_urgency_column = gtk.TreeViewColumn("Urgente?", pixbuf_renderer, pixbuf=0)
        self.append_column(product_urgency_column)
        product_name_column = gtk.TreeViewColumn("Producto", text_renderer, text=1)
        self.append_column(product_name_column)
        product_quantity_column = gtk.TreeViewColumn("Cantidad", text_renderer, text=2)
        self.append_column(product_quantity_column)
        product_ordered_column = gtk.TreeViewColumn("Pedido?", toggle_renderer)
        product_ordered_column.add_attribute(toggle_renderer, "active", 3)
        self.append_column(product_ordered_column)

        # self.connect("cursor-changed", self.on_select_changed, model)
        self.connect("select-cursor-row", self.on_select_cursor_row, model)
        
    def on_product_ordered_toggled(self, cell, path, model):
        model[path][3] = not model[path][3]

    def on_select_cursor_row(self, treeview, start_editing, model):
        treeiter = self.get_selection().get_selected()[1]
        model.remove(treeiter)

