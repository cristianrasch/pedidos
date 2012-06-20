# -*- coding: UTF-8 -*-

import os
import sqlite3
import calendar

from contextlib import contextmanager, closing

class DAO(object):
    instancecount = 0
    conn = None
  
    def __init__(self):
        self.__class__.establishconn()
        self.__class__.instancecount += 1
    
    @classmethod
    def establishconn(cls):
        if not cls.conn:
            env = os.environ["PY_ENV"] if os.environ.has_key("PY_ENV") else "development"
            if env == "test":
                connstr = ":memory:"
            else:
                dirname = os.path.dirname(__file__)
                filename = "%s.db" % env
                connstr = os.path.join(dirname, filename)
            cls.conn = sqlite3.connect(connstr)
            cls.conn.row_factory = sqlite3.Row
            if env == "test":
                cls.conn.executescript("""
                    BEGIN TRANSACTION;
                    CREATE TABLE order_products (id INTEGER PRIMARY KEY, isordered NUMERIC, 
                                                 created_at NUMERIC, isurgent NUMERIC, name TEXT, 
                                                 ordered_on NUMERIC, quantity NUMERIC, 
                                                 updated_at NUMERIC);
                    CREATE INDEX ordered_on_idx ON order_products(ordered_on ASC);
                    COMMIT;
                                       """)
    
    @contextmanager
    def dbquery(self):
        with closing(self.conn.cursor()) as cur:
          yield cur
          self.__class__.conn.commit()
    
    def __del__(self):
        self.__class__.instancecount -= 1
        if not self.__class__.instancecount:
            self.__class__.conn.close()
            self.__class__.conn = None

    def tearDown(self): pass

