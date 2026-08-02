#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🐪 Bou.Bel v2.0 - Tunisian Arabic Programming Language
Main Entry Point
"""

import sys
import os
import argparse
import io
from pathlib import Path

# ============================================
# CORRECTION D'ENCODAGE POUR WINDOWS
# ============================================
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass

    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['LANG'] = 'en_US.UTF-8'

# Ajouter src au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    # ==========================
    # DÉTECTION DU MODE PACKAGE MANAGER
    # ==========================
    if len(sys.argv) > 1 and sys.argv[1] == 'package':
        from src.package_manager.cli import main as pkg_main
        sys.argv = [sys.argv[0]] + sys.argv[2:]
        pkg_main()
        return

    # ==========================
    # PARSER PRINCIPAL
    # ==========================
    parser = argparse.ArgumentParser(description="Bou.Bel - Tunisian Arabic Programming Language")

    parser.add_argument('file', nargs='?', help='Bou.Bel file to execute')
    parser.add_argument('-i', '--interactive', action='store_true', help='Start interactive REPL')
    parser.add_argument('-v', '--version', action='store_true', help='Show version')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--optimize', action='store_true', help='Enable AST optimizations')
    parser.add_argument('--llvm', action='store_true', help='Compile with LLVM compiler')
    parser.add_argument('-o', '--output', help='Output file name')
    parser.add_argument('--debug-compiler', action='store_true', help='Enable compiler debug mode')
    parser.add_argument('--vm', action='store_true', help='Run program using Virtual Machine')
    parser.add_argument('--debug-vm', action='store_true', help='Enable VM debug mode')

    args = parser.parse_args()

    # Show version
    if args.version:
        print("Bou.Bel v2.0 - Tunisian Arabic Programming Language")
        print("Virtual Machine: available")
        print("LLVM Compiler: available")
        return

    # Show help
    if not args.file and not args.interactive:
        print("""
    Bou.Bel v2.0 - Tunisian Arabic Programming Language

    Usage:
      python main.py <file.bou>          - Run a Bou.Bel file (interpreter)
      python main.py --vm <file.bou>     - Run using Virtual Machine
      python main.py --llvm <file.bou>   - Compile to native with LLVM
      python main.py package <command>   - Package manager
      python main.py -i                  - Start interactive REPL
      python main.py -v                  - Show version
      python main.py --debug <file>      - Run with debug mode
      python main.py --optimize <file>   - Run with AST optimizations
        """)
        return

    # ==========================
    # MODE VIRTUAL MACHINE (VM)
    # ==========================
    if args.vm:
        if not args.file:
            print("Please specify a file to run with VM")
            sys.exit(1)

        if not os.path.exists(args.file):
            print(f"File '{args.file}' not found")
            sys.exit(1)

        try:
            from src.lexer.tokenizer import Tokenizer
            from src.parser.parser import Parser
            from src.vm.compiler import Compiler as VMCompiler
            from src.vm.vm import VM

            with open(args.file, 'r', encoding='utf-8') as f:
                code = f.read()

            print(f"Running with VM: {args.file}")
            print("-" * 50)
            if args.optimize:
                print("AST optimizations enabled.")
            print("Compiling to bytecode...")

            tokenizer = Tokenizer(code)
            tokens = tokenizer.tokenize()

            if args.debug or args.debug_vm:
                print(f"Tokens: {len(tokens)}")
                for t in tokens[:10]:
                    print(f"  {t}")

            parser_obj = Parser(tokens)
            ast = parser_obj.parse()

            if args.debug or args.debug_vm:
                print(f"AST: {ast}")

            compiler = VMCompiler()
            bytecode = compiler.compile(ast)

            if args.debug_vm:
                bytecode.disassemble()

            print("Executing bytecode...")

            # ----- Chemins de recherche pour les modules -----
            script_dir = os.path.dirname(os.path.abspath(args.file))
            project_root = os.path.dirname(os.path.abspath(__file__))
            stdlib_dir = os.path.join(project_root, 'stdlib')

            search_paths = [
                script_dir,
                stdlib_dir,
                os.getcwd()
            ]

            vm = VM(search_paths=search_paths)
            output = vm.run(bytecode, debug=args.debug_vm)

            print("-" * 50)
            print("✅ Program executed successfully with VM")

        except ImportError as e:
            print(f"❌ Import error: {e}")
            print("   Make sure all VM modules are present:")
            print("   - src/vm/bytecode.py, src/vm/compiler.py, src/vm/vm.py")
            sys.exit(1)
        except Exception as e:
            print(f"❌ VM execution failed: {e}")
            if args.debug or args.debug_vm:
                import traceback
                traceback.print_exc()
            sys.exit(1)

        return

    # ==========================
    # MODE LLVM (Compilation native)
    # ==========================
    if args.llvm:
        if not args.file:
            print("Please specify a file to compile")
            sys.exit(1)

        if not os.path.exists(args.file):
            print(f"File '{args.file}' not found")
            sys.exit(1)

        debug_mode = args.debug or args.debug_compiler

        try:
            from src.lexer.tokenizer import Tokenizer
            from src.parser.parser import Parser
            from src.compiler.llvm_compiler import LLVMCompiler

            with open(args.file, 'r', encoding='utf-8') as f:
                code = f.read()

            print(f"Compiling: {args.file}")
            print("-" * 50)
            print("Using LLVM compiler...")
            if args.optimize:
                print("AST optimizations enabled.")
            print("Generating LLVM code...")

            tokenizer = Tokenizer(code)
            tokens = tokenizer.tokenize()

            if debug_mode:
                print(f"Tokens: {len(tokens)}")
                for t in tokens[:10]:
                    print(f"  {t}")

            parser_obj = Parser(tokens)
            ast = parser_obj.parse()

            if debug_mode:
                print(f"AST: {ast}")

            compiler = LLVMCompiler(optimize=args.optimize, debug=debug_mode)

            output_file = args.output
            if output_file is None:
                base_name = os.path.splitext(args.file)[0]
                if os.name == 'nt':
                    output_file = base_name + '.exe'
                else:
                    output_file = base_name + '.out'
            else:
                if os.name == 'nt' and not output_file.endswith('.exe'):
                    output_file += '.exe'
                elif os.name != 'nt' and not output_file.endswith('.out'):
                    output_file += '.out'

            result = compiler.compile(ast, output_file)

            if result and os.path.exists(result):
                print(f"✅ Compiled successfully: {result}")
            else:
                print("❌ Compilation failed.")
                sys.exit(1)

        except ImportError as e:
            print(f"❌ Import error: {e}")
            print("   Make sure all required modules are installed:")
            print("   - llvmlite: pip install llvmlite")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Compilation failed: {e}")
            if debug_mode:
                import traceback
                traceback.print_exc()
            sys.exit(1)

        return

    # ==========================
    # MODE INTERPRÉTEUR (AST Walker)
    # ==========================
    if args.file:
        if not os.path.exists(args.file):
            print(f"File '{args.file}' not found")
            sys.exit(1)

        try:
            from src.lexer.tokenizer import Tokenizer
            from src.parser.parser import Parser
            from src.interpreter.interpreter import Interpreter

            with open(args.file, 'r', encoding='utf-8') as f:
                code = f.read()

            print(f"Running: {args.file}")
            print("-" * 50)
            if args.optimize:
                print("AST optimizations enabled.")

            tokenizer = Tokenizer(code)
            tokens = tokenizer.tokenize()

            if args.debug:
                print("\nTokens:")
                for token in tokens:
                    print(f"  {token}")
                print()

            parser_obj = Parser(tokens)
            ast = parser_obj.parse()

            if args.debug:
                print("\nAST:")
                print(ast)
                print()

            interpreter = Interpreter(optimize=args.optimize, debug=args.debug)

            # ----- Définition des chemins de recherche de modules -----
            script_dir = os.path.dirname(os.path.abspath(args.file))
            project_root = os.path.dirname(os.path.abspath(__file__))
            stdlib_dir = os.path.join(project_root, 'stdlib')

            interpreter.module_search_paths = [
                script_dir,
                stdlib_dir,
                os.getcwd()
            ]

            interpreter.interpret(ast)

            print("-" * 50)
            print("Program executed successfully")

        except ImportError as e:
            print(f"❌ Import error: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}")
            if args.debug:
                import traceback
                traceback.print_exc()
            sys.exit(1)

        return

    # ==========================
    # MODE REPL
    # ==========================
    if args.interactive:
        try:
            from src.cli.repl import REPL
            repl = REPL(debug=args.debug)
            repl.start()
        except ImportError:
            print("REPL not available")
            sys.exit(1)


if __name__ == "__main__":
    main()