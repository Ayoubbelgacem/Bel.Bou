# src/vm/cache.py

class VariableCache:
    """Cache des variables pour accès rapide"""
    def __init__(self):
        self.cache = {}
        self.hits = 0
        self.misses = 0
    
    def get(self, name):
        if name in self.cache:
            self.hits += 1
            return self.cache[name]
        self.misses += 1
        return None
    
    def set(self, name, value):
        self.cache[name] = value
    
    def invalidate(self, name=None):
        if name:
            if name in self.cache:
                del self.cache[name]
        else:
            self.cache.clear()
    
    def get_stats(self):
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {
            'hits': self.hits,
            'misses': self.misses,
            'total': total,
            'hit_rate': hit_rate
        }