#!/usr/bin/env python3
"""
Script de compilation du runtime Bou.Bel
Compile en bibliothèques dynamique et statique
"""

import os
import sys
import subprocess
from pathlib import Path

def build_runtime():
    """Compile le runtime en bibliothèques dynamique et statique"""
    runtime_dir = Path(__file__).parent
    c_file = runtime_dir / 'boubel_runtime.c'
    
    if not c_file.exists():
        print(f"❌ Source file not found: {c_file}")
        return False
    
    success = True
    
    # Supprimer les fichiers anciens
    for f in ['libboubel_runtime.dll', 'libboubel_runtime.so', 'libboubel_runtime.a', 'boubel_runtime.o']:
        try:
            os.remove(runtime_dir / f)
        except:
            pass
    
    # 1. Compiler en DLL (dynamique)
    if os.name == 'nt':
        dll_file = runtime_dir / 'libboubel_runtime.dll'
        cmd_dll = [
            'gcc', '-shared',
            '-o', str(dll_file),
            str(c_file),
            '-fPIC', '-O2'
        ]
        print(f"🔧 Compiling DLL: {' '.join(cmd_dll)}")
        result = subprocess.run(cmd_dll, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ DLL compilation failed:")
            print(result.stderr)
            success = False
        else:
            print(f"✅ DLL compiled: {dll_file}")
    
    # 2. Compiler en bibliothèque statique
    try:
        obj_file = runtime_dir / 'boubel_runtime.o'
        lib_file = runtime_dir / 'libboubel_runtime.a'
        
        cmd_obj = ['gcc', '-c', str(c_file), '-o', str(obj_file)]
        print(f"🔧 Compiling object: {' '.join(cmd_obj)}")
        result = subprocess.run(cmd_obj, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Object compilation failed:")
            print(result.stderr)
            success = False
        else:
            cmd_lib = ['ar', 'rcs', str(lib_file), str(obj_file)]
            print(f"🔧 Creating static library: {' '.join(cmd_lib)}")
            result = subprocess.run(cmd_lib, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ Static library creation failed:")
                print(result.stderr)
                success = False
            else:
                print(f"✅ Static library compiled: {lib_file}")
            
            try:
                os.remove(obj_file)
            except:
                pass
                
    except Exception as e:
        print(f"⚠️  Static library compilation skipped: {e}")
    
    return success

if __name__ == '__main__':
    success = build_runtime()
    sys.exit(0 if success else 1)