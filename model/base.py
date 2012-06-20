# -*- coding: UTF-8 -*-

from collections import defaultdict

class Model(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)    
        self.errors = Errors(self)
  
    def attr_name(self, name): return name

    def isvalid(self): return self.errors.isempty()

    def save(self): return self.isvalid()
  

class Errors(object):
    def __init__(self, model):
        self.model = model        
        self.buffer = defaultdict(lambda: [])
    
    def isempty(self):
        return len(self.buffer) == 0

    def add(self, attr, err):
        self.buffer[attr].append(err)
    
    def on(self, attr):
        return self.buffer[attr]

    def fullmessages(self):
        errors = ["%s %s" % (self.model.attr_name(attr), ", ".join(errors)) for attr, errors in self.buffer.items()]
        return "\n".join(errors)

    def clear(self): self.buffer.clear()
