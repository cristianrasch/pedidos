# -*- coding: UTF-8 -*-

import gtk
import os

curr_dir = os.path.dirname(__file__)
def relative_path(path):
    return os.path.join(curr_dir, *path.split("/"))

class App(object):
    def __init__(self):
        self.build_from_glade_xml()
        self.init_product_quantity()
        self.build_product_view()
        
    def build_from_glade_xml(self):
        self.builder = gtk.Builder()
        glade_xml = relative_path("ui.glade")
        self.builder.add_from_file(glade_xml)
        self.builder.connect_signals(self)
        
    def init_product_quantity(self):
      quantity = self.builder.get_object("cantidad")
      quantity.set_value(1)
      
    def build_product_view(self):
      window = self.builder.get_object("scrolledwindow")
      window.add(ProductView())
      window.show_all()
        
    def run(self):
        self.builder.get_object("window").show()
        gtk.main()
    
    def on_window_delete_event(self, widget, data=None):
        gtk.main_quit()
        return False


class ProductModel(gtk.ListStore):
  def __init__(self):
    super(ProductModel, self).__init__(gtk.gdk.Pixbuf, str, int, "gboolean")
    icon_path = relative_path("images/star.png")
    star_icon = gtk.gdk.pixbuf_new_from_file(icon_path)
    for i in xrange(10):
      icon = star_icon if (i%2)!=0 else None
      product_name = "Producto #%d" % (i+1)
      self.append([icon, product_name, i+1, (i%2)==0])
      

class ProductView(gtk.TreeView):
    def __init__(self):
        model = ProductModel()
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
        
    def on_product_ordered_toggled(self, cell, path, model):
        model[path][3] = not model[path][3]

        
        
