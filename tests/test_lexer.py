# tests/test_lexer.py
import sys
import os

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.lexer.lexer import Lexer
from src.lexer.token import TokenType

def test_lexer():
    # Test code with ALL keywords
    code = """
    # Test program
    khdem x = 5;
    khdem name: string = "Ayoub";
    khdem score: int = 10;
    khdem active: bool = s7i7;
    
    ken x > 3 a3mel {
        ikteb("x is big");
    } sinon {
        ikteb("x is small");
    }
    
    i men 1 7ata 5 a3mel {
        ikteb("Number: " + i);
    }
    
    dallel add(a, b) {
        rejje a + b;
    }
    
    class Animal {
        hetha.name = "Unknown";
    }
    
    class Dog toroth Animal {
        jdid() {
            super("Dog");
        }
    }
    
    7awel {
        ikteb("Trying...");
    } ebsed(e) {
        ikteb("Error: " + e);
    } akhir {
        ikteb("Finally!");
    }
    
    import "math";
    """
    
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    
    print("=" * 60)
    print("Bou.Bel Lexer Test Results:")
    print("=" * 60)
    
    # Show all tokens with line numbers
    for token in tokens:
        print(f"Line {token.line:2d}, Col {token.column:2d}: {token}")
    
    print("=" * 60)
    print(f"Total Tokens: {len(tokens)}")
    print("=" * 60)
    
    # Count keyword types
    keyword_count = {}
    for token in tokens:
        if token.type == TokenType.KEYWORD:
            keyword = token.value
            keyword_count[keyword] = keyword_count.get(keyword, 0) + 1
    
    if keyword_count:
        print("\nKeywords found:")
        for kw, count in keyword_count.items():
            print(f"  {kw}: {count}")

if __name__ == "__main__":
    test_lexer()