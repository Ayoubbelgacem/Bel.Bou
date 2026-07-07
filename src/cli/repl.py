import sys
import traceback
import os

# Gestion de readline pour Windows
try:
    import readline
    READLINE_AVAILABLE = True
except ImportError:
    READLINE_AVAILABLE = False
    # Sur Windows, on utilise une alternative
    try:
        import pyreadline
        READLINE_AVAILABLE = True
    except ImportError:
        pass

from src.lexer.lexer import Lexer
from src.parser.parser import Parser
from src.interpreter.interpreter import Interpreter
from src.utils.errors import BouBelError

class REPL:
    def __init__(self, debug=False):
        self.interpreter = Interpreter()
        self.interpreter.debug = debug
        self.debug = debug
        self.history = []
        self.history_file = ".boubel_history"
        self.load_history()
    
    def load_history(self):
        if READLINE_AVAILABLE:
            try:
                readline.read_history_file(self.history_file)
            except FileNotFoundError:
                pass
            except Exception:
                pass
    
    def save_history(self):
        if READLINE_AVAILABLE:
            try:
                readline.write_history_file(self.history_file)
            except Exception:
                pass
    
    def start(self):
        print("=" * 60)
        print("🐪 Bou.Bel v2.0 - Tunisian Arabic Programming Language")
        print("=" * 60)
        print("Commands:")
        print("  help          - Show this help")
        print("  exit / quit   - Exit the REPL")
        print("  clear         - Clear the screen")
        print("  debug         - Toggle debug mode")
        print("  vars          - Show all variables")
        print("  funcs         - Show all functions")
        print("=" * 60)
        print()
        
        while True:
            try:
                # Multi-line input support
                code_lines = []
                while True:
                    try:
                        if not code_lines:
                            line = input(">>> ")
                        else:
                            line = input("... ")
                        
                        if line.strip() == '' and code_lines:
                            break
                        
                        code_lines.append(line)
                        
                        # Check if code is complete
                        if self.is_complete('\n'.join(code_lines)):
                            break
                    except KeyboardInterrupt:
                        print()
                        code_lines = []
                        break
                
                if not code_lines:
                    continue
                
                code = '\n'.join(code_lines)
                
                # Check for special commands
                if code.strip() == 'exit' or code.strip() == 'quit':
                    self.save_history()
                    print("👋 Goodbye!")
                    break
                elif code.strip() == 'help':
                    self.show_help()
                    continue
                elif code.strip() == 'clear':
                    os.system('cls' if os.name == 'nt' else 'clear')
                    continue
                elif code.strip() == 'debug':
                    self.debug = not self.debug
                    self.interpreter.debug = self.debug
                    print(f"🐛 Debug mode: {'ON' if self.debug else 'OFF'}")
                    continue
                elif code.strip() == 'vars':
                    self.show_variables()
                    continue
                elif code.strip() == 'funcs':
                    self.show_functions()
                    continue
                
                # Execute the code
                try:
                    lexer = Lexer(code)
                    tokens = lexer.tokenize(debug=self.debug)
                    
                    parser = Parser(tokens)
                    ast = parser.parse()
                    
                    if self.debug:
                        print("📊 AST:")
                        self.print_ast(ast, 0)
                    
                    # Execute in REPL mode
                    result = self.interpreter.interpret(ast, is_repl=True)
                    
                    # Store in history
                    self.history.append(code)
                    self.save_history()
                    
                except BouBelError as e:
                    print(f"❌ {e}")
                except SyntaxError as e:
                    print(f"❌ Syntax Error: {e}")
                except Exception as e:
                    print(f"❌ Error: {e}")
                    if self.debug:
                        traceback.print_exc()
                
            except KeyboardInterrupt:
                print()
                continue
            except EOFError:
                print()
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                if self.debug:
                    traceback.print_exc()
    
    def is_complete(self, code):
        """Check if the code is syntactically complete"""
        # Simple check: count braces and parentheses
        stack = []
        for char in code:
            if char in '([{':
                stack.append(char)
            elif char in ')]}':
                if not stack:
                    return False
                last = stack.pop()
                if (char == ')' and last != '(') or \
                   (char == ']' and last != '[') or \
                   (char == '}' and last != '{'):
                    return False
        
        # If we have unclosed braces, code is incomplete
        if stack:
            return False
        
        # Check if the code ends with a semicolon or block
        code = code.strip()
        if code.endswith(';') or code.endswith('}') or code.endswith('{'):
            return True
        
        # If it's a single expression without semicolon, it's complete
        if ';' in code or '\n' in code:
            return True
        
        # Check for incomplete statements
        keywords = ['ken', 'tawa', 'men', 'dallel', 'class', '7awel', 'khdem', 'ikteb']
        for keyword in keywords:
            if keyword in code and not code.endswith('}'):
                # Check if it's a complete statement
                if code.strip().endswith(';'):
                    return True
                return False
        
        return True
    
    def show_help(self):
        print("""
📖 Bou.Bel Language Guide
=======================

Variables:
  khdem x = 10;
  khdem nom = "Ahmed";

Printing:
  ikteb("Hello World");
  ikteb(x);

Input:
  khdem age = iqra("Enter age: ");

Conditions:
  ken x > 10 a3mel {
      ikteb("x is greater than 10");
  } sinon_ken x == 10 a3mel {
      ikteb("x equals 10");
  } sinon {
      ikteb("x is less than 10");
  }

Loops:
  i men 1 7ata 5 a3mel {
      ikteb(i);
  }
  
  tawa x < 10 a3mel {
      ikteb(x);
      x = x + 1;
  }

Functions:
  dallel add(x, y) {
      rejje x + y;
  }
  
  khdem result = add(5, 3);

Classes:
  class Person {
      khdem name = "";
      khdem age = 0;
      
      function jdid(n, a) {
          hetha.name = n;
          hetha.age = a;
      }
      
      function greet() {
          ikteb("Hello, " + hetha.name);
      }
  }

File I/O:
  ikteb_fi_mlf("data.txt", "Hello World");
  khdem content = iqra_mlf("data.txt");

REPL Commands:
  help    - Show this help
  vars    - Show all variables
  funcs   - Show all functions
  debug   - Toggle debug mode
  clear   - Clear screen
  exit    - Exit REPL
        """)
    
    def show_variables(self):
        print("\n📦 Variables:")
        print("-" * 40)
        vars = self.interpreter.current_env.get_all_variables()
        if not vars:
            print("  (none)")
        else:
            for name, value in vars.items():
                if not name.startswith('__'):
                    print(f"  {name}: {value} (type: {type(value).__name__})")
        print()
    
    def show_functions(self):
        print("\n🔧 Functions:")
        print("-" * 40)
        funcs = self.interpreter.current_env.get_all_functions()
        if not funcs:
            print("  (none)")
        else:
            for name, func in funcs.items():
                if isinstance(func, dict):
                    params = func.get('params', [])
                    print(f"  {name}({', '.join(params)})")
                else:
                    print(f"  {name} (built-in)")
        print()
    
    def print_ast(self, node, indent=0):
        """Pretty print the AST for debugging"""
        if node is None:
            return
        
        prefix = "  " * indent
        node_type = node.__class__.__name__
        
        print(f"{prefix}└── {node_type}")
        
        if hasattr(node, 'name') and node.name is not None:
            print(f"{prefix}    ├── name: {node.name}")
        if hasattr(node, 'value') and node.value is not None:
            print(f"{prefix}    ├── value: {node.value}")
        if hasattr(node, 'params') and node.params is not None:
            print(f"{prefix}    ├── params: {node.params}")
        if hasattr(node, 'body') and node.body is not None:
            print(f"{prefix}    ├── body:")
            if isinstance(node.body, list):
                for child in node.body:
                    self.print_ast(child, indent + 2)
            else:
                self.print_ast(node.body, indent + 2)
        if hasattr(node, 'then_body') and node.then_body is not None:
            print(f"{prefix}    ├── then_body:")
            for child in node.then_body:
                self.print_ast(child, indent + 2)
        if hasattr(node, 'else_body') and node.else_body is not None:
            print(f"{prefix}    └── else_body:")
            for child in node.else_body:
                self.print_ast(child, indent + 2)