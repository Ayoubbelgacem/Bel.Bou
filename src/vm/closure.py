# src/vm/closure.py

class Closure:
    """Représente une closure (fonction + environnement capturé)"""
    def __init__(self, function, env):
        self.function = function
        self.env = env
        self.params = function.get('params', [])
        self.body = function.get('body', [])
        self.start = function.get('start', 0)
    
    def __repr__(self):
        return f"Closure(func={self.function.get('name', 'anonymous')}, env={len(self.env)})"

class Environment:
    """Environnement pour la VM avec support des closures"""
    def __init__(self, parent=None):
        self.parent = parent
        self.variables = {}
        self.constants = {}
    
    def get(self, name):
        if name in self.variables:
            return self.variables[name]
        if name in self.constants:
            return self.constants[name]
        if self.parent:
            return self.parent.get(name)
        return None
    
    def get_local(self, name):
        if name in self.variables:
            return self.variables[name]
        if name in self.constants:
            return self.constants[name]
        return None
    
    def set(self, name, value):
        if self.parent and self.parent.get_local(name) is not None:
            self.parent.set(name, value)
            return
        self.variables[name] = value
    
    def define(self, name, value, is_constant=False):
        if is_constant:
            self.constants[name] = value
        else:
            self.variables[name] = value
    
    def create_child(self):
        return Environment(self)
    
    def copy(self):
        new_env = Environment(self.parent)
        new_env.variables = self.variables.copy()
        new_env.constants = self.constants.copy()
        return new_env