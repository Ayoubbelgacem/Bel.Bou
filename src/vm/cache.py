class VariableCache:
    """Cache des variables pour accès rapide avec limite de taille"""
    
    def __init__(self, max_size=1000):
        self.cache = {}
        self.hits = 0
        self.misses = 0
        self.max_size = max_size
        self.access_order = []  # ✅ Suivi de l'ordre d'accès
    
    def get(self, name):
        if name in self.cache:
            self.hits += 1
            # ✅ Mettre à jour l'ordre d'accès (LRU)
            if name in self.access_order:
                self.access_order.remove(name)
            self.access_order.append(name)
            return self.cache[name]
        self.misses += 1
        return None
    
    def set(self, name, value):
        # ✅ Limiter la taille de la cache (LRU)
        if name not in self.cache and len(self.cache) >= self.max_size:
            # Supprimer l'élément le moins récemment utilisé
            if self.access_order:
                oldest = self.access_order.pop(0)
                if oldest in self.cache:
                    del self.cache[oldest]
        
        self.cache[name] = value
        if name in self.access_order:
            self.access_order.remove(name)
        self.access_order.append(name)
    
    def invalidate(self, name=None):
        if name:
            if name in self.cache:
                del self.cache[name]
            if name in self.access_order:
                self.access_order.remove(name)
        else:
            self.cache.clear()
            self.access_order.clear()
    
    def get_stats(self):
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {
            'hits': self.hits,
            'misses': self.misses,
            'total': total,
            'hit_rate': hit_rate,
            'cache_size': len(self.cache),
            'max_size': self.max_size
        }
    
    def clear(self):
        """Vider complètement le cache"""
        self.cache.clear()
        self.access_order.clear()
        self.hits = 0
        self.misses = 0