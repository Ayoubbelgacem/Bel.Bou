# Contribuer à Bou.Bel

Merci de contribuer au projet Bou.Bel ! Voici quelques lignes directrices pour vous aider à commencer.

## Comment contribuer

1. **Forker** le dépôt sur GitHub
2. **Créer une branche** pour votre fonctionnalité
   ```bash
   git checkout -b feature/ma-fonctionnalite
   ```
3. **Développer** et **tester** vos modifications
4. **Soumettre une pull request**

## Structure du projet

```
src/
├── lexer/          # Analyse lexicale (Tokenizer)
├── parser/         # Analyse syntaxique (Parser)
├── interpreter/    # Interpréteur (Interpreter)
├── compiler/       # Compilateur LLVM (LLVMCompiler)
├── optimizer/      # Optimisations AST (ASTOptimizer)
└── cli/            # Interface ligne de commande (REPL)

tools/
├── vscode-extension/ # Extension VSCode
├── debugger/         # Débogueur
└── tests/            # Tests unitaires

runtime/            # Runtime C pour le compilateur LLVM
examples/           # Exemples de programmes
docs/               # Documentation
```

## Lancer les tests

```bash
# Avec pytest (recommandé)
python scripts/run_tests.py

# Ou manuellement
python tools/tests/run_all_tests.py
```

## Standards de code

- Python 3.8+
- PEP 8 pour le style
- Docstrings pour les fonctions (format Google ou Sphinx)
- Tests pour les nouvelles fonctionnalités

### Exemple de docstring
```python
def addition(a, b):
    """Additionne deux nombres.

    Args:
        a: Premier nombre
        b: Deuxième nombre

    Returns:
        La somme de a et b
    """
    return a + b
```

## Ajouter une nouvelle fonctionnalité

### Exemple : Ajouter une nouvelle fonction built-in

1. Ajouter la fonction dans `src/interpreter/interpreter.py` :
```python
def call_builtin(self, name, args):
    # ...
    elif name == "nouvelle_fonction":
        # Implémentation
```

2. Ajouter des tests dans `tools/tests/test_interpreter.py`
3. Mettre à jour la documentation dans `docs/api_reference.md`

## Signaler un bug

Utilisez les issues GitHub en incluant :
- Version de Bou.Bel
- Système d'exploitation
- Code minimal pour reproduire le bug
- Comportement attendu vs réel

## Questions

Pour toute question, contactez-nous via les discussions GitHub ou par email.

---

**Merci de contribuer à Bou.Bel !** 🇹🇳🐪✨