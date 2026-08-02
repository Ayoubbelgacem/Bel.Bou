"""
Débogueur simple pour Bou.Bel
Permet d'exécuter pas à pas, d'inspecter les variables, etc.
"""

import sys
import readline
from src.parser.ast import *


class Debugger:
    """
    Débogueur interactif pour Bou.Bel
    """

    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.breakpoints = []
        self.step_mode = False
        self.current_line = 0
        self.source_lines = []
        self.bp_counter = 1

    def set_breakpoint(self, line_number):
        """Ajoute un point d'arrêt"""
        if line_number not in self.breakpoints:
            self.breakpoints.append(line_number)
            self.breakpoints.sort()
            print(f"✅ Point d'arrêt ajouté à la ligne {line_number}")
        else:
            print(f"⚠️ Point d'arrêt déjà présent à la ligne {line_number}")

    def remove_breakpoint(self, line_number):
        """Supprime un point d'arrêt"""
        if line_number in self.breakpoints:
            self.breakpoints.remove(line_number)
            print(f"✅ Point d'arrêt supprimé à la ligne {line_number}")
        else:
            print(f"⚠️ Aucun point d'arrêt à la ligne {line_number}")

    def list_breakpoints(self):
        """Liste les points d'arrêt"""
        if self.breakpoints:
            print("📌 Points d'arrêt:")
            for bp in self.breakpoints:
                print(f"  - Ligne {bp}")
        else:
            print("📌 Aucun point d'arrêt défini")

    def run(self, node):
        """Exécute le programme avec le débogueur"""
        if hasattr(node, 'statements'):
            for stmt in node.statements:
                self.visit_stmt(stmt)
        else:
            self.visit_stmt(node)

    def visit_stmt(self, stmt):
        """Visite un statement avec débogage"""
        if stmt is None:
            return

        self.current_line += 1

        # Vérifier si point d'arrêt
        if self.current_line in self.breakpoints:
            print(f"\n🔴 Point d'arrêt à la ligne {self.current_line}")
            self._debug_prompt(stmt)

        # Exécuter le statement
        try:
            self.interpreter.visit(stmt)
        except Exception as e:
            print(f"❌ Erreur à la ligne {self.current_line}: {e}")
            self._debug_prompt(stmt, error=str(e))
            raise

    def _debug_prompt(self, stmt, error=None):
        """Affiche le prompt de débogage"""
        while True:
            try:
                cmd = input("(dbg) ").strip()
                if cmd == "":
                    continue

                if cmd in ['c', 'continue']:
                    return

                elif cmd in ['n', 'next']:
                    return

                elif cmd in ['s', 'step']:
                    self.step_mode = True
                    return

                elif cmd in ['p', 'print']:
                    if error:
                        print(f"Erreur: {error}")
                    else:
                        print("Environnement:", self.interpreter.environment)

                elif cmd in ['v', 'variables']:
                    if self.interpreter.environment:
                        print("Variables:")
                        for k, v in self.interpreter.environment.items():
                            print(f"  {k} = {v}")
                    else:
                        print("Aucune variable")

                elif cmd in ['b', 'break']:
                    parts = cmd.split()
                    if len(parts) == 2:
                        try:
                            line = int(parts[1])
                            self.set_breakpoint(line)
                        except ValueError:
                            print(f"❌ Ligne invalide: {parts[1]}")
                    else:
                        print("Utilisation: break <ligne>")

                elif cmd in ['bl', 'breakpoints']:
                    self.list_breakpoints()

                elif cmd in ['d', 'delete']:
                    parts = cmd.split()
                    if len(parts) == 2:
                        try:
                            line = int(parts[1])
                            self.remove_breakpoint(line)
                        except ValueError:
                            print(f"❌ Ligne invalide: {parts[1]}")
                    else:
                        self.breakpoints = []
                        print("✅ Tous les points d'arrêt supprimés")

                elif cmd in ['q', 'quit']:
                    print("👋 Sortie du débogueur")
                    sys.exit(0)

                elif cmd in ['h', 'help']:
                    self._show_help()

                else:
                    print(f"❌ Commande inconnue: {cmd}")
                    self._show_help()

            except KeyboardInterrupt:
                print("\n👋 Sortie du débogueur")
                sys.exit(0)
            except EOFError:
                print("\n👋 Sortie du débogueur")
                sys.exit(0)

    def _show_help(self):
        """Affiche l'aide du débogueur"""
        print("""
        Commandes du débogueur:
        ──────────────────────────────────────
        c, continue   - Continuer l'exécution
        n, next       - Passer à la ligne suivante
        s, step       - Entrer dans la fonction
        p, print      - Afficher l'environnement
        v, variables  - Afficher les variables
        b <ligne>     - Ajouter un point d'arrêt
        bl, breakpoints - Lister les points d'arrêt
        d <ligne>     - Supprimer un point d'arrêt
        d             - Supprimer tous les points d'arrêt
        q, quit       - Quitter le débogueur
        h, help       - Afficher cette aide
        """)