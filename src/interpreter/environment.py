# src/interpreter/environment.py

class Environment:
    """
    Gestionnaire d'environnement pour l'interpréteur Bou.Bel.
    Gère les variables, fonctions, classes et la portée.
    """
    
    def __init__(self, parent=None):
        """
        Initialise un nouvel environnement.
        
        Args:
            parent (Environment, optional): Environnement parent pour la portée.
        """
        self.parent = parent
        self.variables = {}
        self.constants = {}
        self.functions = {}
        self.classes = {}
        self.objects = {}
        self.imports = {}
        self._locked = False
    
    # ========== GESTION DES VARIABLES ==========
    
    def get(self, name):
        """
        Récupère une variable de l'environnement.
        Recherche d'abord dans l'environnement courant, puis dans les parents.
        
        Args:
            name (str): Nom de la variable
            
        Returns:
            La valeur de la variable ou None si non trouvée
        """
        if name in self.variables:
            return self.variables[name]
        if name in self.constants:
            return self.constants[name]
        if self.parent:
            return self.parent.get(name)
        return None
    
    def get_local(self, name):
        """
        Récupère une variable UNIQUEMENT dans l'environnement courant (sans remonter).
        
        Args:
            name (str): Nom de la variable
            
        Returns:
            La valeur de la variable ou None si non trouvée
        """
        if name in self.variables:
            return self.variables[name]
        if name in self.constants:
            return self.constants[name]
        return None
    
    def set(self, name, value):
        """
        Définit une variable dans l'environnement courant.
        
        Args:
            name (str): Nom de la variable
            value: Valeur à assigner
        """
        if self._locked:
            raise Exception("❌ Environment is locked")
        
        # Vérifier si c'est une constante
        if name in self.constants:
            raise Exception(f"❌ Cannot reassign constant '{name}'")
        
        # Vérifier si la variable existe dans un parent
        if self.parent and self.parent.get_local(name) is not None:
            self.parent.set(name, value)
            return
        
        self.variables[name] = value
    
    def define(self, name, value, is_constant=False):
        """
        Définit une nouvelle variable dans l'environnement courant.
        
        Args:
            name (str): Nom de la variable
            value: Valeur à assigner
            is_constant (bool): Si True, la variable est constante
        """
        if self._locked:
            raise Exception("❌ Environment is locked")
        
        if is_constant:
            self.constants[name] = value
        else:
            self.variables[name] = value
    
    def define_const(self, name, value):
        """
        Définit une constante.
        
        Args:
            name (str): Nom de la constante
            value: Valeur de la constante
        """
        if self._locked:
            raise Exception("❌ Environment is locked")
        self.constants[name] = value
    
    def has(self, name):
        """
        Vérifie si une variable existe dans l'environnement ou ses parents.
        
        Args:
            name (str): Nom de la variable
            
        Returns:
            bool: True si la variable existe
        """
        if name in self.variables or name in self.constants:
            return True
        if self.parent:
            return self.parent.has(name)
        return False
    
    def has_local(self, name):
        """
        Vérifie si une variable existe UNIQUEMENT dans l'environnement courant.
        
        Args:
            name (str): Nom de la variable
            
        Returns:
            bool: True si la variable existe
        """
        return name in self.variables or name in self.constants
    
    def delete(self, name):
        """
        Supprime une variable de l'environnement courant.
        
        Args:
            name (str): Nom de la variable
            
        Returns:
            bool: True si la variable a été supprimée
        """
        if self._locked:
            raise Exception("❌ Environment is locked")
        
        if name in self.variables:
            del self.variables[name]
            return True
        if name in self.constants:
            del self.constants[name]
            return True
        if self.parent:
            return self.parent.delete(name)
        return False
    
    # ========== GESTION DES FONCTIONS ==========
    
    def get_function(self, name):
        """
        Récupère une fonction de l'environnement.
        
        Args:
            name (str): Nom de la fonction
            
        Returns:
            La fonction ou None si non trouvée
        """
        if name in self.functions:
            return self.functions[name]
        if self.parent:
            return self.parent.get_function(name)
        return None
    
    def get_function_local(self, name):
        """
        Récupère une fonction UNIQUEMENT dans l'environnement courant.
        
        Args:
            name (str): Nom de la fonction
            
        Returns:
            La fonction ou None si non trouvée
        """
        return self.functions.get(name)
    
    def define_function(self, name, func):
        """
        Définit une fonction dans l'environnement courant.
        
        Args:
            name (str): Nom de la fonction
            func: La fonction (callable ou objet fonction)
        """
        if self._locked:
            raise Exception("❌ Environment is locked")
        self.functions[name] = func
    
    def has_function(self, name):
        """
        Vérifie si une fonction existe.
        
        Args:
            name (str): Nom de la fonction
            
        Returns:
            bool: True si la fonction existe
        """
        if name in self.functions:
            return True
        if self.parent:
            return self.parent.has_function(name)
        return False
    
    # ========== GESTION DES CLASSES ==========
    
    def get_class(self, name):
        """
        Récupère une classe de l'environnement.
        
        Args:
            name (str): Nom de la classe
            
        Returns:
            La classe ou None si non trouvée
        """
        if name in self.classes:
            return self.classes[name]
        if self.parent:
            return self.parent.get_class(name)
        return None
    
    def define_class(self, name, cls):
        """
        Définit une classe dans l'environnement courant.
        
        Args:
            name (str): Nom de la classe
            cls: La classe
        """
        if self._locked:
            raise Exception("❌ Environment is locked")
        self.classes[name] = cls
    
    def has_class(self, name):
        """
        Vérifie si une classe existe.
        
        Args:
            name (str): Nom de la classe
            
        Returns:
            bool: True si la classe existe
        """
        if name in self.classes:
            return True
        if self.parent:
            return self.parent.has_class(name)
        return False
    
    # ========== GESTION DES OBJETS ==========
    
    def get_object(self, id):
        """
        Récupère un objet par son ID.
        
        Args:
            id: ID de l'objet
            
        Returns:
            L'objet ou None si non trouvé
        """
        if id in self.objects:
            return self.objects[id]
        if self.parent:
            return self.parent.get_object(id)
        return None
    
    def define_object(self, id, obj):
        """
        Définit un objet dans l'environnement courant.
        
        Args:
            id: ID de l'objet
            obj: L'objet
        """
        if self._locked:
            raise Exception("❌ Environment is locked")
        self.objects[id] = obj
    
    # ========== GESTION DES IMPORTS ==========
    
    def get_import(self, name):
        """
        Récupère un module importé.
        
        Args:
            name (str): Nom du module
            
        Returns:
            Le module ou None si non trouvé
        """
        if name in self.imports:
            return self.imports[name]
        if self.parent:
            return self.parent.get_import(name)
        return None
    
    def define_import(self, name, module):
        """
        Définit un module importé.
        
        Args:
            name (str): Nom du module
            module: Le module importé
        """
        if self._locked:
            raise Exception("❌ Environment is locked")
        self.imports[name] = module
    
    # ========== GESTION DE LA PORTÉE ==========
    
    def create_child(self):
        """
        Crée un environnement enfant.
        
        Returns:
            Environment: Nouvel environnement enfant
        """
        return Environment(self)
    
    def enter_scope(self):
        """
        Entre dans une nouvelle portée (alias de create_child).
        
        Returns:
            Environment: Nouvel environnement
        """
        return self.create_child()
    
    def exit_scope(self):
        """
        Sort de la portée courante et retourne à l'environnement parent.
        
        Returns:
            Environment: Environnement parent
        """
        if self.parent:
            return self.parent
        return self
    
    # ========== UTILITAIRES ==========
    
    def get_all_variables(self):
        """
        Récupère toutes les variables de l'environnement (y compris les parents).
        
        Returns:
            dict: Dictionnaire de toutes les variables
        """
        result = {}
        
        # Récupérer les variables des parents
        if self.parent:
            result.update(self.parent.get_all_variables())
        
        # Ajouter les variables locales
        result.update(self.variables)
        
        return result
    
    def get_all_functions(self):
        """
        Récupère toutes les fonctions de l'environnement (y compris les parents).
        
        Returns:
            dict: Dictionnaire de toutes les fonctions
        """
        result = {}
        
        if self.parent:
            result.update(self.parent.get_all_functions())
        
        result.update(self.functions)
        
        return result
    
    def get_all_classes(self):
        """
        Récupère toutes les classes de l'environnement (y compris les parents).
        
        Returns:
            dict: Dictionnaire de toutes les classes
        """
        result = {}
        
        if self.parent:
            result.update(self.parent.get_all_classes())
        
        result.update(self.classes)
        
        return result
    
    def clear(self):
        """
        Vide l'environnement courant (sans affecter les parents).
        """
        if self._locked:
            raise Exception("❌ Environment is locked")
        self.variables.clear()
        self.constants.clear()
        self.functions.clear()
        self.classes.clear()
        self.objects.clear()
        self.imports.clear()
    
    def lock(self):
        """
        Verrouille l'environnement (empêche les modifications).
        """
        self._locked = True
    
    def unlock(self):
        """
        Déverrouille l'environnement.
        """
        self._locked = False
    
    def is_locked(self):
        """
        Vérifie si l'environnement est verrouillé.
        
        Returns:
            bool: True si verrouillé
        """
        return self._locked
    
    def copy(self):
        """
        Crée une copie superficielle de l'environnement.
        
        Returns:
            Environment: Copie de l'environnement
        """
        new_env = Environment(self.parent)
        new_env.variables = self.variables.copy()
        new_env.constants = self.constants.copy()
        new_env.functions = self.functions.copy()
        new_env.classes = self.classes.copy()
        new_env.objects = self.objects.copy()
        new_env.imports = self.imports.copy()
        return new_env
    
    # ========== REPRÉSENTATION ==========
    
    def __repr__(self):
        return f"Environment(vars={len(self.variables)}, consts={len(self.constants)}, funcs={len(self.functions)}, classes={len(self.classes)})"
    
    def __str__(self):
        lines = []
        lines.append("=" * 60)
        lines.append("ENVIRONMENT")
        lines.append("=" * 60)
        
        if self.variables:
            lines.append("📦 Variables:")
            for name, value in self.variables.items():
                lines.append(f"  {name}: {value} (type: {type(value).__name__})")
        
        if self.constants:
            lines.append("🔒 Constants:")
            for name, value in self.constants.items():
                lines.append(f"  {name}: {value} (type: {type(value).__name__})")
        
        if self.functions:
            lines.append("🔧 Functions:")
            for name in self.functions.keys():
                lines.append(f"  {name}()")
        
        if self.classes:
            lines.append("📚 Classes:")
            for name in self.classes.keys():
                lines.append(f"  {name}")
        
        if self.objects:
            lines.append("🎯 Objects:")
            for id, obj in self.objects.items():
                class_name = obj.get('__class__', 'Unknown') if isinstance(obj, dict) else type(obj).__name__
                lines.append(f"  {id}: {class_name}")
        
        if self.imports:
            lines.append("📦 Imports:")
            for name in self.imports.keys():
                lines.append(f"  {name}")
        
        if self.parent:
            lines.append("")
            lines.append("⬆️ Parent Environment:")
            lines.append(str(self.parent))
        
        return "\n".join(lines)

# ========== CLASSES D'EXCEPTION ==========

class EnvironmentError(Exception):
    """Exception levée pour les erreurs d'environnement"""
    pass

class VariableNotFoundError(EnvironmentError):
    """Exception levée quand une variable n'est pas trouvée"""
    def __init__(self, name):
        self.name = name
        super().__init__(f"Variable '{name}' not found in environment")

class ConstantReassignmentError(EnvironmentError):
    """Exception levée quand on tente de modifier une constante"""
    def __init__(self, name):
        self.name = name
        super().__init__(f"Cannot reassign constant '{name}'")

class EnvironmentLockedError(EnvironmentError):
    """Exception levée quand l'environnement est verrouillé"""
    def __init__(self):
        super().__init__("Environment is locked, cannot modify")

# ========== FONCTION D'USINE ==========

def create_global_environment():
    """
    Crée un environnement global avec les variables et fonctions par défaut.
    
    Returns:
        Environment: Environnement global configuré
    """
    env = Environment()
    
    # Variables globales par défaut
    env.define_const("__version__", "2.0.0")
    env.define_const("__author__", "Bou.Bel Team")
    
    # Constantes mathématiques
    env.define_const("PI", 3.141592653589793)
    env.define_const("E", 2.718281828459045)
    
    return env