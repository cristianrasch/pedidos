# -*- coding: UTF-8 -*-

import sqlite3
import calendar
from datetime import date, datetime, timedelta
from operator import attrgetter

from base import Model
from pedidos.db.dao import DAO

class OrderProductDAO(DAO):
    def __init__(self):
        super(self.__class__, self).__init__()

    def save(self, order_product):
        try:
            with self.dbquery() as cur:
                if order_product.id:
                    sql = """
                        UPDATE order_products set name=?, quantity=?, isurgent=?, 
                                                  isordered=?, updated_at=?
                        WHERE id=?
                    """
                    today = datetime.today()
                    updated_at = calendar.timegm(today.utctimetuple())
                    cur.execute(sql, (order_product.name, order_product.quantity, 
                                      order_product.isurgent, order_product.isordered, 
                                      updated_at, order_product.id))
                    return cur.rowcount
                else:                
                    sql = """
                        INSERT INTO order_products (ordered_on, name, quantity, isurgent, isordered, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """
                    ordered_on = order_product.ordered_on.toordinal()
                    today = datetime.today()
                    created_at = calendar.timegm(today.utctimetuple())
                    cur.execute(sql, (ordered_on, order_product.name, 
                                      order_product.quantity, order_product.isurgent, 
                                      order_product.isordered, created_at, created_at))
                    return cur.lastrowid
        except sqlite3.Error:
            return 0

    def find_by_ordered_on_and_name(self, ordered_on, name):
        with self.dbquery() as cur:
            sql = """
                SELECT * FROM order_products
                WHERE ordered_on = ? AND
                      name = ? COLLATE NOCASE
                ORDER BY created_at DESC
            """
            cur.execute(sql, (ordered_on.toordinal(), name))
            return cur.fetchone()

    def find_all_by_ordered_on(self, ordered_on):
        with self.dbquery() as cur:
            sql = """
                SELECT * FROM order_products
                WHERE ordered_on = ?
                ORDER BY isurgent DESC, created_at ASC
            """
            cur.execute(sql, (ordered_on.toordinal(),))
            return cur.fetchall()

    def delete(self, order_product):
        with self.dbquery() as cur:
            sql = """
                DELETE FROM order_products
                WHERE id = ?
            """
            cur.execute(sql, (order_product.id,))
            return cur.rowcount

    def find_all_not_ordered_before(self, date):
        with self.dbquery() as cur:
            sql = """
                SELECT * FROM order_products
                WHERE ordered_on < ? AND
                      isordered = ?
                ORDER BY created_at ASC
            """
            cur.execute(sql, (date.toordinal(), 0))
            return cur.fetchall()

    def mass_update_ordered_on(self, date, order_product_ids):
        with self.dbquery() as cur:
            sql = """
                UPDATE order_products
                SET ordered_on = ?
                WHERE id IN (%s)
            """ % ",".join("?"*len(order_product_ids))
            cur.execute(sql, (date.toordinal(),) + tuple(order_product_ids))
            return cur.rowcount

    def find_all_unique_names_ordered_between(self, ordered_on_from, ordered_on_to):
        with self.dbquery() as cur:
            sql = """
                SELECT DISTINCT name COLLATE NOCASE
                FROM order_products
                WHERE ordered_on >= ? AND
                      ordered_on <= ?
                ORDER BY name ASC
            """
            cur.execute(sql, (ordered_on_from.toordinal(), ordered_on_to.toordinal()))
            return map(lambda row: row["name"], cur.fetchall())

    def tearDown(self):
        with self.dbquery() as cur:
            cur.execute("DELETE FROM order_products")

class OrderProduct(Model):
    dao = OrderProductDAO()

    def __init__(self, **kwargs):
        Model.__init__(self, **kwargs)
        if not hasattr(self, "id"): self.id = 0
        if not hasattr(self, "ordered_on"): self.ordered_on = date.today()
        if not hasattr(self, "name"): self.name = ""
        if not hasattr(self, "quantity"): self.quantity = 1
        if not hasattr(self, "isurgent"): self.isurgent = False
        if not hasattr(self, "isordered"): self.isordered = False

    def attr_name(self, attr):
        if attr == "ordered_on": return "Fecha"
        if attr == "name": return "Producto"
        return Model.attr_name(self, attr)

    def isvalid(self):
        self.errors.clear()

        if self.ordered_on < date.today():
            self.errors.add("ordered_on", "debe ser igual o posterior a la fecha actual")
        
        if not len(self.name.strip()): 
            self.errors.add("name", "no puede estar en blanco")

        if self.isnewrecord() and self.find_by_ordered_on_and_name(self.ordered_on, self.name):
            self.errors.add("name", "ya ha sido pedido en esa fecha")

        return super(self.__class__, self).isvalid()

    def save(self, validate=True): 
        if not validate or self.isvalid():
            id = self.dao.save(self)
            if id:
                self.id = id                
                return True

    def delete(self):
        return self.dao.delete(self)

    def __eq__(self, other):
        return self.id == other.id    

    def isnewrecord(self):
        return not self.id

    def toggle_isordered(self):
        self.isordered = not self.isordered

    @classmethod    
    def find_by_ordered_on_and_name(cls, ordered_on, name):
        row = cls.dao.find_by_ordered_on_and_name(ordered_on, name)
        if row: return cls.new(row)

    @classmethod
    def find_all_by_ordered_on(cls, ordered_on):
        rows = cls.dao.find_all_by_ordered_on(ordered_on)
        return map(lambda row: cls.new(row), rows)

    @classmethod
    def find_all_not_yet_ordered_on(cls, ordered_on):
        order_products = cls.find_all_by_ordered_on(ordered_on)
        return filter(lambda order_product: not order_product.isordered, order_products)

    @classmethod
    def find_all_not_ordered_before(cls, date):
        rows = cls.dao.find_all_not_ordered_before(date)
        return map(lambda row: cls.new(row), rows)

    @classmethod
    def reorder_pending_products(cls):
        today = date.today()
        pending_products = cls.find_all_not_ordered_before(today)

        if pending_products:
            order_product_ids = map(lambda product: product.id, pending_products)
            return cls.dao.mass_update_ordered_on(today, order_product_ids)

    @classmethod
    def find_all_unique_names_ordered_last_month(cls):
        today = date.today()
        a_month_ago = today - timedelta(weeks=4)
        return cls.dao.find_all_unique_names_ordered_between(a_month_ago, today)

    @classmethod
    def new(cls, row):
        if row:
            product = cls()
            product.id = row["id"]
            product.ordered_on = date.fromordinal(row["ordered_on"])
            product.name = row["name"]
            product.quantity = row["quantity"]
            product.isurgent = row["isurgent"]
            product.isordered = row["isordered"]
            return product
