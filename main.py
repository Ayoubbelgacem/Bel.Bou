#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import argparse

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.lexer.lexer import Lexer
from src.parser.parser import Parser
from src.interpreter.interpreter import Interpreter
from src.cli.repl import REPL
from src.utils.errors import BouBelError

# Import VM components
try:
    from src.vm.compiler import Compiler
    from src.vm.vm import VM
    VM_AVAILABLE = True
except ImportError:
    VM_AVAILABLE = False


def run_file(filename, debug=False):
    """Execute a Bou.Bel file using the Interpreter"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            code = f.read()
        
        print(f"📂 Running: {filename}")
        print("-" * 50)
        
        # Lexer
        lexer = Lexer(code)
        tokens = lexer.tokenize(debug=debug)
        
        # Parser
        parser = Parser(tokens)
        ast = parser.parse()
        
        # Interpreter
        interpreter = Interpreter()
        interpreter.debug = debug
        interpreter.interpret(ast)
        
        print("-" * 50)
        print("✅ Program executed successfully")
        
    except FileNotFoundError:
        print(f"❌ File '{filename}' not found")
        sys.exit(1)
    except BouBelError as e:
        print(f"❌ {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def run_file_with_vm(filename, debug=False):
    """Execute a Bou.Bel file using the Virtual Machine"""
    if not VM_AVAILABLE:
        print("❌ VM module not available. Please check your installation.")
        sys.exit(1)
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            code = f.read()
        
        print(f"📂 Running: {filename} (VM)")
        print("-" * 50)
        
        # Lexer
        lexer = Lexer(code)
        tokens = lexer.tokenize(debug=debug)
        
        # Parser
        parser = Parser(tokens)
        ast = parser.parse()
        
        # Compiler
        compiler = Compiler()
        bytecode = compiler.compile(ast)
        
        if debug:
            bytecode.disassemble()
        
        # VM
        vm = VM()
        vm.run(bytecode, debug=debug)
        
        print("-" * 50)
        print("✅ Program executed successfully (VM)")
        
    except FileNotFoundError:
        print(f"❌ File '{filename}' not found")
        sys.exit(1)
    except BouBelError as e:
        print(f"❌ {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def show_help():
    """Display help message with examples"""
    print("""
        🐪 Bou.Bel v2.0 - Tunisian Arabic Programming Language
        
        Usage:
          python main.py <file.bou>     - Run a Bou.Bel file
          python main.py -i            - Start interactive REPL
          python main.py -v            - Show version
          python main.py --debug <file> - Run with debug mode
          python main.py --vm <file>   - Run with Virtual Machine
          python main.py --debug-vm <file> - Run VM with debug mode
        
        Example Bou.Bel code:
          khdem x = 10;
          khdem y = 20;
          khdem z = x + y;
          ikteb(z);  // Affiche 30
          
          ken z > 25 a3mel {
              ikteb("z est grand");
          } sinon {
              ikteb("z est petit");
          }
        
        For more information, visit: https://github.com/boubel-lang
        """)


def show_version():
    """Display version information"""
    print("🐪 Bou.Bel v2.0 - Tunisian Arabic Programming Language")
    print("Copyright © 2024 Bou.Bel Team")
    print("")
    print("Features:")
    print("  ✅ Lexer & Parser")
    print("  ✅ Interpreter")
    if VM_AVAILABLE:
        print("  ✅ Virtual Machine (VM)")
    else:
        print("  ❌ Virtual Machine (VM) - Not available")
    print("  ✅ OOP (Classes, Inheritance)")
    print("  ✅ Arrays & Strings")
    print("  ✅ File I/O")
    print("  ✅ Try/Catch/Finally")
    print("  ✅ REPL (Interactive Shell)")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="🐪 Bou.Bel - Tunisian Arabic Programming Language",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py test.bou        - Run a Bou.Bel file
  python main.py -i              - Start interactive REPL
  python main.py -v              - Show version
  python main.py --debug test.bou - Run with debug output
  python main.py --vm test.bou   - Run with Virtual Machine
  python main.py --debug-vm test.bou - Run VM with debug output
        """
    )
    
    # Arguments
    parser.add_argument('file', nargs='?', help='Bou.Bel file to execute')
    parser.add_argument('-i', '--interactive', action='store_true', help='Start interactive REPL')
    parser.add_argument('-v', '--version', action='store_true', help='Show version')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode (tokens, AST)')
    parser.add_argument('--vm', action='store_true', help='Use Virtual Machine instead of Interpreter')
    parser.add_argument('--debug-vm', action='store_true', help='Enable VM debug mode')
    
    args = parser.parse_args()
    
    # Show version
    if args.version:
        show_version()
        return
    
    # Show help if no arguments
    if not args.file and not args.interactive:
        show_help()
        return
    
    # Run file
    if args.file:
        # Check if file exists
        if not os.path.exists(args.file):
            print(f"❌ File '{args.file}' not found")
            sys.exit(1)
        
        # Run with VM or Interpreter
        if args.vm:
            if not VM_AVAILABLE:
                print("❌ VM module not available. Please check your installation.")
                sys.exit(1)
            run_file_with_vm(args.file, debug=args.debug or args.debug_vm)
        else:
            run_file(args.file, debug=args.debug or args.debug_vm)
    
    # Start REPL
    elif args.interactive:
        debug_mode = args.debug or args.debug_vm
        if args.vm:
            print("⚠️  VM mode not supported in REPL. Using Interpreter.")
        repl = REPL(debug=debug_mode)
        repl.start()


if __name__ == "__main__":
    main()