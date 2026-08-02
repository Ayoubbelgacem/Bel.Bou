# src/compiler/optimizer.py
"""
Optimiseur LLVM pour le code généré
"""

import llvmlite.binding as llvm

class Optimizer:
    """
    Optimiseur LLVM
    Applique des passes d'optimisation sur le module
    """
    
    def __init__(self, optimization_level=2):
        """
        Initialise l'optimiseur
        
        Args:
            optimization_level: Niveau d'optimisation (0-3)
        """
        self.optimization_level = optimization_level
    
    def optimize_module(self, module):
        """
        Optimise un module LLVM
        
        Args:
            module: Module LLVM à optimiser
        
        Returns:
            Module optimisé
        """
        # Créer le pass manager
        pmb = llvm.create_pass_manager_builder()
        pmb.opt_level = self.optimization_level
        pmb.size_level = 0
        
        # Ajouter les passes d'optimisation
        pm = llvm.create_module_pass_manager()
        pmb.populate(pm)
        
        # Exécuter les optimisations
        pm.run(module)
        
        return module
    
    def optimize_function(self, function):
        """
        Optimise une fonction LLVM
        
        Args:
            function: Fonction à optimiser
        
        Returns:
            Fonction optimisée
        """
        # Pour optimiser une fonction individuelle
        # On crée un module temporaire
        module = function.module
        self.optimize_module(module)
        return function
    
    def optimize_ir(self, ir_code):
        """
        Optimise du code IR
        
        Args:
            ir_code: Code LLVM IR à optimiser
        
        Returns:
            Code IR optimisé
        """
        # Parser le code IR
        module = llvm.parse_assembly(ir_code)
        
        # Optimiser
        self.optimize_module(module)
        
        # Retourner le code IR optimisé
        return str(module)