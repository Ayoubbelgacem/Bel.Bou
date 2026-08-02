# Installation de Bou.Bel

## Prérequis

- Python 3.8 ou supérieur
- GCC ou Clang (pour la compilation)
- (Optionnel) LLVM 14+ pour le compilateur natif

## Installation sur Windows

### 1. Installer Python
Téléchargez Python depuis [python.org](https://www.python.org/downloads/) et installez-le.

### 2. Installer GCC (via MSYS2)
```bash
# Télécharger MSYS2 depuis https://www.msys2.org/
# Puis dans le terminal MSYS2 :
pacman -S mingw-w64-ucrt-x86_64-gcc
```

### 3. Cloner Bou.Bel
```bash
git clone https://github.com/Ayoubbelgacem/Bel.Bou.git
cd Bel.Bou
```

### 4. Créer un environnement virtuel
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 5. Installer les dépendances
```bash
pip install llvmlite
```

### 6. Compiler le runtime
```bash
cd runtime
python build_runtime.py
cd ..
```

## Installation sur Linux

### 1. Installer Python et GCC
```bash
sudo apt update
sudo apt install python3 python3-pip build-essential
```

### 2. Installer LLVM
```bash
sudo apt install llvm
```

### 3. Cloner et installer
```bash
git clone https://github.com/Ayoubbelgacem/Bel.Bou.git
cd Bel.Bou
python3 -m venv .venv
source .venv/bin/activate
pip install llvmlite
cd runtime && python3 build_runtime.py && cd ..
```

## Vérification

```bash
python main.py --help
# Devrait afficher l'aide
```

## Problèmes courants

### Erreur: "llvmlite not found"
```bash
pip install llvmlite
```

### Erreur: "GCC not found"
- Windows : Installer MSYS2
- Linux : `sudo apt install build-essential`

### Erreur: "Runtime library not found"
```bash
cd runtime
python build_runtime.py
cd ..
```

## Prochaine étape

👉 [Guide de démarrage](guide.md)