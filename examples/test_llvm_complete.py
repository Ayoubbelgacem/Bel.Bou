#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧪 Test LLVM simplifié et corrigé pour Bou.Bel
"""

import os
import sys
import subprocess
from pathlib import Path

# Ajouter src au chemin
sys.path.insert(0, str(Path(__file__).parent))

# Couleurs (sans emojis pour éviter les problèmes d'encodage)
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(text):
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}{BLUE}{text.center(60)}{RESET}")
    print(f"{BOLD}{BLUE}{'='*60}{RESET}")

def print_success(text):
    print(f"{GREEN}[OK] {text}{RESET}")

def print_error(text):
    print(f"{RED}[FAIL] {text}{RESET}")

def print_info(text):
    print(f"{YELLOW}[INFO] {text}{RESET}")

def print_warning(text):
    print(f"{YELLOW}[WARN] {text}{RESET}")

def run_command(cmd, timeout=30):
    """
    Exécute une commande avec support UTF-8
    Version corrigée pour éviter les problèmes d'encodage
    """
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
            errors="replace",
            timeout=timeout
        )
        
        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0
        }
    except subprocess.TimeoutExpired:
        return {
            "returncode": -1,
            "stdout": "",
            "stderr": "Timeout",
            "success": False
        }
    except Exception as e:
        return {
            "returncode": -1,
            "stdout": "",
            "stderr": str(e),
            "success": False
        }

def test_llvm_available():
    """Test si LLVM est disponible"""
    print_header("Test: Verification LLVM")
    
    try:
        import llvmlite
        print_success(f"LLVM disponible - Version: {llvmlite.__version__}")
        return True
    except ImportError as e:
        print_error(f"LLVM non disponible: {e}")
        print_info("Installez avec: pip install llvmlite")
        return False

def test_simple_compilation():
    """Test de compilation simple"""
    print_header("Test: Compilation simple")
    
    # Créer un fichier de test SIMPLE avec les bons mots-clés
    test_file = "test_simple.bou"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write("""
khdem x = 10;
khdem y = 20;
khdem z = x + y;
ikteb(z);
""")
    
    output = "test_simple"
    if os.name == 'nt':
        output += '.exe'
    
    cmd = f"python main.py --llvm {test_file} -o {output}"
    print_info(f"Commande: {cmd}")
    
    result = run_command(cmd)
    
    if result["success"] and os.path.exists(output):
        print_success(f"Compilation reussie: {output}")
        
        # Exécuter le binaire
        run_cmd = f"./{output}" if os.name != 'nt' else output
        exec_result = run_command(run_cmd)
        
        if exec_result["success"]:
            print_success("Execution reussie!")
            output_lines = exec_result["stdout"].strip().split('\n')
            for line in output_lines:
                print(f"  Output: {line}")
        else:
            print_error(f"Execution echouee: {exec_result['stderr']}")
        
        # Nettoyer
        try:
            os.remove(test_file)
            os.remove(output)
        except:
            pass
        
        return True
    else:
        print_error("Compilation echouee")
        if result["stderr"]:
            print(f"  stderr: {result['stderr'][:500]}")
        if result["stdout"]:
            print(f"  stdout: {result['stdout'][:500]}")
        return False

def test_compilation_with_conditions():
    """Test avec conditions"""
    print_header("Test: Compilation avec conditions")
    
    test_file = "test_conditions.bou"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write("""
khdem x = 15;
ken x > 10 a3mel {
    ikteb(100);
} sinon {
    ikteb(0);
}
""")
    
    output = "test_conditions"
    if os.name == 'nt':
        output += '.exe'
    
    cmd = f"python main.py --llvm {test_file} -o {output}"
    result = run_command(cmd)
    
    if result["success"] and os.path.exists(output):
        print_success("Compilation reussie!")
        
        # Exécuter
        run_cmd = f"./{output}" if os.name != 'nt' else output
        exec_result = run_command(run_cmd)
        
        if exec_result["success"]:
            print_success(f"Execution: {exec_result['stdout'].strip()}")
        else:
            print_error(f"Execution echouee: {exec_result['stderr']}")
        
        try:
            os.remove(test_file)
            os.remove(output)
        except:
            pass
        return True
    else:
        print_error("Compilation echouee")
        if result["stderr"]:
            print(f"  stderr: {result['stderr'][:500]}")
        return False

def test_compilation_with_loop():
    """Test avec boucle"""
    print_header("Test: Compilation avec boucle")
    
    test_file = "test_loop.bou"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write("""
khdem i = 0;
khdem sum = 0;
min i < 5 a3mel {
    sum = sum + i;
    i = i + 1;
}
ikteb(sum);
""")
    
    output = "test_loop"
    if os.name == 'nt':
        output += '.exe'
    
    cmd = f"python main.py --llvm {test_file} -o {output}"
    result = run_command(cmd)
    
    if result["success"] and os.path.exists(output):
        print_success("Compilation reussie!")
        
        run_cmd = f"./{output}" if os.name != 'nt' else output
        exec_result = run_command(run_cmd)
        
        if exec_result["success"]:
            print_success(f"Execution: {exec_result['stdout'].strip()}")
        else:
            print_error(f"Execution echouee: {exec_result['stderr']}")
        
        try:
            os.remove(test_file)
            os.remove(output)
        except:
            pass
        return True
    else:
        print_error("Compilation echouee")
        if result["stderr"]:
            print(f"  stderr: {result['stderr'][:500]}")
        return False

def test_compilation_with_function():
    """Test avec fonction"""
    print_header("Test: Compilation avec fonction")
    
    test_file = "test_function.bou"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write("""
dallel carre(n) {
    raje3 n * n;
}

khdem x = carre(5);
ikteb(x);
""")
    
    output = "test_function"
    if os.name == 'nt':
        output += '.exe'
    
    cmd = f"python main.py --llvm {test_file} -o {output}"
    result = run_command(cmd)
    
    if result["success"] and os.path.exists(output):
        print_success("Compilation reussie!")
        
        run_cmd = f"./{output}" if os.name != 'nt' else output
        exec_result = run_command(run_cmd)
        
        if exec_result["success"]:
            print_success(f"Execution: {exec_result['stdout'].strip()}")
        else:
            print_error(f"Execution echouee: {exec_result['stderr']}")
        
        try:
            os.remove(test_file)
            os.remove(output)
        except:
            pass
        return True
    else:
        print_error("Compilation echouee")
        if result["stderr"]:
            print(f"  stderr: {result['stderr'][:500]}")
        return False

def test_llvm_ir_generation():
    """Test de génération IR"""
    print_header("Test: Generation IR")
    
    test_file = "test_ir.bou"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write("khdem x = 42; ikteb(x);")
    
    # Compiler avec debug pour voir l'IR
    cmd = f"python main.py --llvm --debug-compiler {test_file}"
    print_info(f"Commande: {cmd}")
    
    result = run_command(cmd)
    
    if result["success"]:
        # Vérifier que l'IR est présent
        if "define" in result["stdout"] or "define" in result["stderr"]:
            print_success("Generation IR reussie!")
            
            # Extraire les lignes intéressantes
            output = result["stdout"] + result["stderr"]
            lines = [l for l in output.split('\n') if 'define' in l or 'ret i' in l or 'alloca' in l]
            
            print("  Apercu du IR genere:")
            for line in lines[:10]:
                if line.strip():
                    print(f"    {line.strip()[:100]}")
            
            try:
                os.remove(test_file)
            except:
                pass
            return True
        else:
            print_error("IR non trouve dans la sortie")
            return False
    else:
        print_error("Generation IR echouee")
        if result["stderr"]:
            print(f"  stderr: {result['stderr'][:500]}")
        return False

def test_multiple_operations():
    """Test avec plusieurs opérations"""
    print_header("Test: Operations multiples")
    
    test_file = "test_ops.bou"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write("""
khdem a = 10;
khdem b = 20;
khdem c = a + b;
khdem d = c * 2;
khdem e = d - 5;
ikteb(e);
""")
    
    output = "test_ops"
    if os.name == 'nt':
        output += '.exe'
    
    cmd = f"python main.py --llvm {test_file} -o {output}"
    result = run_command(cmd)
    
    if result["success"] and os.path.exists(output):
        print_success("Compilation reussie!")
        
        run_cmd = f"./{output}" if os.name != 'nt' else output
        exec_result = run_command(run_cmd)
        
        if exec_result["success"]:
            print_success(f"Execution: {exec_result['stdout'].strip()}")
        else:
            print_error(f"Execution echouee: {exec_result['stderr']}")
        
        try:
            os.remove(test_file)
            os.remove(output)
        except:
            pass
        return True
    else:
        print_error("Compilation echouee")
        if result["stderr"]:
            print(f"  stderr: {result['stderr'][:500]}")
        return False

def main():
    """Fonction principale"""
    print_header("TEST LLVM - Bou.Bel (Version corrigee)")
    
    # Vérifier main.py
    if not os.path.exists("main.py"):
        print_error("main.py non trouve!")
        return
    
    print_info(f"Python: {sys.version}")
    print_info(f"OS: {sys.platform}")
    print_info(f"Repertoire: {os.getcwd()}")
    
    # Vérifier examples
    examples = Path("examples")
    if not examples.exists():
        print_info("Creation du dossier examples...")
        examples.mkdir()
    
    # Tests à exécuter
    tests = [
        ("Verification LLVM", test_llvm_available),
        ("Compilation simple", test_simple_compilation),
        ("Compilation avec conditions", test_compilation_with_conditions),
        ("Compilation avec boucle", test_compilation_with_loop),
        ("Compilation avec fonction", test_compilation_with_function),
        ("Operations multiples", test_multiple_operations),
        ("Generation IR", test_llvm_ir_generation)
    ]
    
    passed = 0
    failed = 0
    results = []
    
    for name, test_func in tests:
        print_header(f"Execution: {name}")
        if test_func():
            passed += 1
            results.append((name, True))
        else:
            failed += 1
            results.append((name, False))
    
    # Résumé détaillé
    print_header("RESULTAT FINAL")
    print(f"Total des tests: {len(tests)}")
    print_success(f"Reussis: {passed}")
    print_error(f"Echoues: {failed}")
    
    # Détail des résultats
    if results:
        print("\n" + "-" * 60)
        for name, status in results:
            if status:
                print(f"  {GREEN}[OK]{RESET} {name}")
            else:
                print(f"  {RED}[FAIL]{RESET} {name}")
    
    # Évaluation
    if failed == 0:
        print_success("\nTOUS LES TESTS ONT REUSSI!")
        print_info("Le compilateur LLVM fonctionne correctement.")
        print_info("\nPour compiler vos fichiers:")
        print_info("  python main.py --llvm votre_fichier.bou -o executable")
    else:
        print_warning(f"\n{failed} tests ont echoue")
        print_info("Vérifiez les erreurs ci-dessus.")
        print_info("\nSolutions possibles:")
        print_info("  1. Installez llc: pacman -S mingw-w64-ucrt-x86_64-llvm")
        print_info("  2. Installez gcc: pacman -S mingw-w64-ucrt-x86_64-gcc")
        print_info("  3. Vérifiez les mots-clés dans vos fichiers .bou")

if __name__ == "__main__":
    main()