import os
import subprocess
import shutil
import sys
from pathlib import Path
from .config import Config

PACKAGE_DIR = os.path.join(os.path.expanduser("~"), ".boubel", "packages")
os.makedirs(PACKAGE_DIR, exist_ok=True)

def install_package(name, version=None, source=None):
    """Installe un paquet depuis un dépôt Git ou un chemin local."""
    target_dir = os.path.join(PACKAGE_DIR, name)
    if os.path.exists(target_dir):
        print(f"📦 Package '{name}' already installed.")
        return

    if source is None:
        # Supposons un dépôt Git conventionnel
        repo = f"https://github.com/boubel-packages/{name}.git"
        if version:
            repo = f"{repo}#{version}"
        print(f"⬇️ Downloading {name} from {repo}")
        try:
            subprocess.run(["git", "clone", repo, target_dir], check=True, capture_output=True)
            print(f"✅ Package '{name}' installed.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {name}: {e.stderr}")
    elif source.startswith(("http://", "https://")):
        # Téléchargement depuis une URL (à implémenter si nécessaire)
        print("HTTP installation not yet implemented.")
    elif os.path.exists(source):
        # Copie depuis un chemin local
        shutil.copytree(source, target_dir)
        print(f"✅ Package '{name}' installed from local path.")
    else:
        print(f"❌ Unknown source: {source}")

def install_all(config=None):
    """Installe toutes les dépendances du projet."""
    if config is None:
        config = Config()
    deps = config.get_dependencies()
    if not deps:
        print("📦 No dependencies found.")
        return
    print("📦 Installing dependencies...")
    for name, version in deps.items():
        install_package(name, version)

def list_installed():
    """Liste les paquets installés."""
    installed = os.listdir(PACKAGE_DIR)
    if not installed:
        print("📦 No packages installed.")
        return
    print("📦 Installed packages:")
    for pkg in installed:
        print(f"  - {pkg}")