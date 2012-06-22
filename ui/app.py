# -*- coding: UTF-8 -*-

import gtk
import os

from datetime import date

from treeview import ProductModel, ProductView
from pedidos.helpers import relative_path
from pedidos.model.order_product import OrderProduct

class App(object):
    def __init__(self):
        self.build_from_glade_xml()
        self.build_product_view()
        self.reset_calendar()
        self.reset_product_quantity()
        
    def build_from_glade_xml(self):
        self.builder = gtk.Builder()
        glade_xml = relative_path("ui/ui.glade")
        self.builder.add_from_file(glade_xml)
        self.builder.connect_signals(self)

        self.window = self.builder.get_object("window")
        self.calendar = self.builder.get_object("calendar")
        self.name = self.builder.get_object("name")
        self.quantity = self.builder.get_object("quantity")
        self.urgency = self.builder.get_object("urgency")
        self.title = self.builder.get_object("title")
      
    def build_product_view(self):
        window = self.builder.get_object("scrolledwindow")
        self.product_view = ProductView()
        self.product_view.connect("cursor-changed", self.on_product_clicked)
        self.product_view.connect("select-cursor-row", self.on_product_double_clicked)
        window.add(self.product_view)
        window.show_all()

    def reset_product_quantity(self):
        self.quantity.set_value(1)

    def reset_calendar(self):
        today = date.today()
        self.calendar.select_month(today.month-1, today.year)
        self.calendar.select_day(today.day)
        
    def run(self):
        reordered_products = OrderProduct.reorder_pending_products()
        if reordered_products:
            self.notify("%d producto(s) agregado(s) al pedido del día" % reordered_products)
            self.on_calendar_day_selected(self.calendar)
        self.window.show()
        gtk.main()
    
    def on_window_delete_event(self, widget, data=None):
        gtk.main_quit()
        return False

    def on_save_clicked(self, widget):
        model, treeiter = self.product_view.get_selected()
        if treeiter:
            order_product = model.get_value(treeiter, ProductModel.PROD_IDX)
        else:
            order_product = OrderProduct(ordered_on=self.calendardate())

        order_product.name = unicode(self.name.get_text(), "utf-8")
        order_product.quantity = self.quantity.get_value()
        order_product.isurgent = self.urgency.get_active()

        if order_product.save():
            if treeiter:
                model.update_order_product(treeiter, order_product)
            else:
                model.append_order_product(order_product)
            
            self.reset_form()
        else:
            self.showerror(order_product.errors.fullmessages())

    def notify(self, message):
        dialog = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, 
                                   gtk.BUTTONS_OK, message)
        dialog.run()
        dialog.destroy()

    def ask(self, question):
        dialog = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION, 
                                   gtk.BUTTONS_YES_NO, question)
        response = dialog.run()
        dialog.destroy()
        return response == gtk.RESPONSE_YES

    def showerror(self, err):
        dialog = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, 
                                   gtk.BUTTONS_CLOSE, err)
        dialog.run()
        dialog.destroy()

    def on_clear_clicked(self, widget):
        self.reset_calendar()
        self.reset_form()

    def reset_form(self):
        self.name.set_text("")
        self.reset_product_quantity()
        self.urgency.set_active(False)

    def calendardate(self):
        year, month, day = self.calendar.get_date()
        return date(year, month+1, day)
        
    def on_calendar_day_selected(self, widget):
        selected_date = self.calendardate()
        self.title.set_text("Pedido del %s" % selected_date.strftime("%d/%m"))
        self.product_view.set_date(selected_date)

    def on_product_clicked(self, treeview):
        treeiter = treeview.get_selected()[1]
        if not treeiter: return
        model = treeview.get_model()
        order_product = model.get_value(treeiter, ProductModel.PROD_IDX)
        if not order_product.isordered:
            self.urgency.set_active(order_product.isurgent)
            self.name.set_text(order_product.name)
            self.quantity.set_value(order_product.quantity)

    def on_product_double_clicked(self, treeview, start_editing):
        treeiter, model = treeview.get_selected()[1], treeview.get_model()
        if not treeiter: 
            return
        order_product = model.get_value(treeiter, ProductModel.PROD_IDX)
        
        if order_product.isordered:
            self.showerror("%s es un producto ya pedido, no se puede eliminar" % order_product.name)
        else:
            confirmed = self.ask("¿Está seguro desea eliminar el producto: %s?" % order_product.name)
            if confirmed and order_product.delete():
                model.remove(treeiter)
