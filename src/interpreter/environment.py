# src/interpreter/environment.py
class Environment:
    def __init__(self, parent=None):
        self.parent = parent
        self.variables = {}
        self.functions = {}
        self.classes = {}
    
    def get(self, name):
        if name in self.variables:
            return self.variables[name]
        if self.parent:
            return self.parent.get(name)
        return None
    
    def set(self, name, value):
        self.variables[name] = value
    
    def define(self, name, value):
        self.variables[name] = value