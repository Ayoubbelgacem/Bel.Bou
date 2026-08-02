#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de vérification des fichiers sources du compilateur LLVM.
Permet de s'assurer que les versions corrigées sont bien en place.
"""

import os
import sys

def main():
    print("🔍 Vérification des fichiers sources :", file=sys.stderr)
    
    targets = [
        "src/compiler/llvm/statements.py",
        "src/compiler/llvm/expressions.py",
        "src/compiler/llvm/control_flow.py",
    ]
    
    all_ok = True
    for f in targets:
        if os.path.exists(f):
            with open(f, 'r', encoding='utf-8') as fp:
                content = fp.read()
                if "VERSION CORRIGÉE" in content or "TRACE" in content:
                    print(f"✅ {f} : présent et contient les traces", file=sys.stderr)
                else:
                    print(f"⚠️ {f} : présent mais semble être l'ancienne version", file=sys.stderr)
                    all_ok = False
        else:
            print(f"❌ {f} : introuvable !", file=sys.stderr)
            all_ok = False

    print("\n📁 Contenu du dossier src/compiler/llvm/ :", file=sys.stderr)
    if os.path.exists("src/compiler/llvm/"):
        for f in sorted(os.listdir("src/compiler/llvm/")):
            if f.endswith(".py"):
                print(f"   - {f}", file=sys.stderr)
    else:
        print("   dossier src/compiler/llvm/ inexistant", file=sys.stderr)
        all_ok = False

    if all_ok:
        print("\n✅ Tous les fichiers semblent corrects.", file=sys.stderr)
    else:
        print("\n⚠️ Certains fichiers sont manquants ou ne sont pas à jour.", file=sys.stderr)

if __name__ == "__main__":
    main()