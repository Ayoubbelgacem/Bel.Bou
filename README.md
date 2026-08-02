# 🐪 Bou.Bel - Langage de programmation tunisien

![Version](https://img.shields.io/badge/version-2.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.8+-yellow)

**Bou.Bel** est un langage de programmation conçu pour permettre aux Tunisiens de programmer dans leur **langue maternelle** (arabe tunisien). Il combine une syntaxe simple et intuitive avec la puissance d'un compilateur LLVM.

## 📚 Caractéristiques

- 🇹🇳 **Syntaxe en arabe tunisien** : `khdem`, `ikteb`, `ken`, `men...7ata`
- 🚀 **Compilation en code natif** via LLVM (exécutables .exe/.out)
- 🐍 **Interpréteur intégré** pour le développement rapide
- 🧬 **Programmation orientée objet** : classes, héritage, constructeurs
- ⚠️ **Gestion des exceptions** : `7awel/ebsed/akhir`
- 📁 **Opérations sur fichiers** : lecture/écriture
- 📦 **Types de base** : int, float, string, bool, array
- 🧪 **Optimisations AST** : constant folding, dead code elimination

## 🚀 Installation

```bash
# Cloner le dépôt
git clone https://github.com/Ayoubbelgacem/Bel.Bou.git
cd Bou.Bel

# Créer un environnement virtuel (recommandé)
python -m venv .venv
source .venv/bin/activate  # Sur Windows : .venv\Scripts\activate

# Installer les dépendances
pip install llvmlite

# Compiler le runtime
cd runtime
python build_runtime.py
cd ..