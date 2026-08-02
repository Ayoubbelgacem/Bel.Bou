# Changelog - Bou.Bel

Toutes les modifications notables du projet Bou.Bel.

## Version 2.0 (2024-07-20)

### Ajouts majeurs
- ✅ **Compilateur LLVM complet** : Génération de code natif (exécutables .exe/.out)
- ✅ **Optimisations AST** : Constant folding et dead code elimination (`--optimize`)
- ✅ **Extension VSCode** : Coloration syntaxique, snippets, autocomplétion
- ✅ **Débogueur intégré** : Points d'arrêt, pas à pas, inspection des variables
- ✅ **Suite de tests unitaires** : pytest pour lexer, parser, interpréteur, compilateur, optimiseur
- ✅ **Documentation complète** : README, guide, syntaxe, API, exemples, contribution

### Améliorations
- 🔧 Affichage des booléens : `True` / `False` (au lieu de `1` / `0`)
- 🔧 Affichage des flottants : `20.0` (au lieu de `20`)
- 🔧 Gestion des exceptions : messages détaillés avec `ebsed(e)`
- 🔧 Performance : Optimisations LLVM et AST
- 🔧 Modularisation du compilateur LLVM en sous-modules

### Corrections de bugs
- 🐛 Correction de l'affichage des booléens dans l'interpréteur
- 🐛 Correction de la division par zéro
- 🐛 Correction des fichiers de l'extension VSCode
- 🐛 Correction des imports dans le compilateur LLVM

## Version 1.5 (2024-06-15)

### Ajouts
- ✅ Programmation orientée objet : classes, héritage, constructeurs
- ✅ Gestion des exceptions : `7awel/ebsed/akhir`
- ✅ Opérations sur fichiers : `ikteb_fi_mlf`, `iqra_mlf`
- ✅ Fonctions built-in : `len`, `str`, `int`, `float`, `type`, `print`, `input`
- ✅ Fonctions sur tableaux : `sum`, `max`, `min`, `range`, `append`, `pop`, `sorted`

### Améliorations
- 🔧 Tableaux : affichage en `[1, 2, 3]`
- 🔧 Chaînes : concaténation avec `+`
- 🔧 Messages d'erreur plus explicites

## Version 1.0 (2024-05-01)

### Ajouts
- ✅ Premier lancement du projet
- ✅ Syntaxe en arabe tunisien : `khdem`, `ikteb`, `ken`, `sinon`
- ✅ Variables et types : int, float, string, bool, char
- ✅ Conditions : `ken`, `sinon_ken`, `sinon`
- ✅ Boucles : `men ... 7ata`, `tawa`
- ✅ Fonctions : `dallel`, `rejje`
- ✅ Tableaux : `[1, 2, 3]`, accès `tab[0]`
- ✅ Interpréteur intégré
- ✅ CLI avec REPL