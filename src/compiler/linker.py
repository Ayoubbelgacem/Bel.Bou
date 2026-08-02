# src/compiler/linker.py
"""
Linker pour créer des exécutables à partir de code objet
"""

import os
import subprocess
import platform

class Linker:
    """
    Linker pour créer des exécutables
    """
    
    def __init__(self):
        """
        Initialise le linker
        """
        self.system = platform.system()
        self.compilers = ['clang', 'gcc', 'cc']
    
    def link(self, obj_file, output_file):
        """
        Lie un fichier objet pour créer un exécutable
        
        Args:
            obj_file: Chemin du fichier objet (.o)
            output_file: Chemin du fichier de sortie (.exe ou .out)
        
        Returns:
            str: Chemin du fichier exécutable
        """
        # Trouver un compilateur disponible
        compiler = self._find_compiler()
        if not compiler:
            raise Exception("No C compiler found (clang, gcc, or cc)")
        
        # Préparer la commande
        if self.system == "Windows":
            if not output_file.endswith('.exe'):
                output_file += '.exe'
        else:
            if not output_file.endswith('.out'):
                output_file += '.out'
        
        cmd = [compiler, obj_file, '-o', output_file]
        
        # Ajouter les librairies
        if self.system != "Windows":
            cmd.append('-lm')  # Math library
        
        if self.debug:
            print(f"🔗 Linking: {' '.join(cmd)}")
        
        # Exécuter le linker
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Linker error:\n{result.stderr}")
                raise Exception(f"Linking failed: {result.stderr}")
        except Exception as e:
            raise Exception(f"Linker execution failed: {e}")
        
        # Supprimer le fichier objet
        try:
            os.remove(obj_file)
        except:
            pass
        
        return output_file
    
    def _find_compiler(self):
        """
        Trouve un compilateur disponible
        
        Returns:
            str: Nom du compilateur ou None
        """
        for compiler in self.compilers:
            try:
                # Vérifier si le compilateur existe
                subprocess.run([compiler, '--version'], 
                             capture_output=True, check=True)
                return compiler
            except:
                continue
        
        return None
    
    def set_debug(self, debug):
        """
        Active ou désactive le mode debug
        
        Args:
            debug: True pour activer le mode debug
        """
        self.debug = debug