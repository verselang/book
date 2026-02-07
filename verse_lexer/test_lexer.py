#!/usr/bin/env python3
"""Debug script to test Verse lexer token output with specific code blocks."""

import re
import os
import sys
from pygments import lex
from pygments.token import Token
from verse import VerseLexer


def print_help():
    """Print usage help message."""
    print("""
Usage: test_lexer.py [OPTIONS]

OPTIONS:
  all                          Test all code blocks (default)
  <number>                     Test specific block (e.g., "01", "16", "21b")
  -f, --file <path>            Use specific markdown file (default: VerseSyntaxValidation.md)
  -h, --help                   Show this help message

EXAMPLES:
  test_lexer.py                    # Test all blocks in VerseSyntaxValidation.md
  test_lexer.py 24a                # Test block 24a
  test_lexer.py -f other.md        # Test all blocks in other.md
  test_lexer.py 08 -f custom.md    # Test block 08 in custom.md
""")


def find_markdown_file(filename):
    """Find markdown file, checking multiple locations."""
    # List of search paths relative to script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    search_paths = [
        filename,  # Current directory
        os.path.join(script_dir, '..', 'docs', filename),  # ../docs/
        os.path.join(script_dir, '..', filename),  # ../
        os.path.join(script_dir, filename),  # Same directory as script
    ]
    
    for path in search_paths:
        if os.path.isfile(path):
            return os.path.abspath(path)
    
    paths_str = '\n  '.join(search_paths)
    raise FileNotFoundError(f"Markdown file not found: {filename}\nSearched in:\n  {paths_str}")


def extract_code_blocks(content):
    """Extract all verse code blocks with their ID comments."""
    # Pattern: <!-- ID --> followed by ```verse ... ```
    pattern = r'<!--\s*(\d+\w?)\s*-->\s*```verse\n(.*?)```'
    matches = re.findall(pattern, content, re.DOTALL)
    return matches


def main():
    # Show help if no arguments provided
    if len(sys.argv) == 1:
        print_help()
        sys.exit(0)
    
    # Parse command line arguments
    block_id = None
    markdown_file = "VerseSyntaxValidation.md"
    
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        
        if arg in ['-h', '--help']:
            print_help()
            sys.exit(0)
        elif arg in ['-f', '--file']:
            if i + 1 < len(sys.argv):
                markdown_file = sys.argv[i + 1]
                i += 2
            else:
                print("Error: --file requires an argument")
                print_help()
                sys.exit(1)
        elif arg.startswith('-'):
            print(f"Error: Unknown option '{arg}'")
            print_help()
            sys.exit(1)
        else:
            block_id = arg
            i += 1
    
    # Set default block_id if not provided
    if block_id is None:
        block_id = "all"
    
    # Find and read markdown file
    try:
        filepath = find_markdown_file(markdown_file)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    # Extract code blocks
    blocks = extract_code_blocks(content)
    
    if not blocks:
        print(f"Error: No code blocks found in {markdown_file}")
        sys.exit(1)
    
    # Filter blocks based on block_id
    if block_id.lower() == "all":
        blocks_to_test = blocks
    else:
        blocks_to_test = [(bid, code) for bid, code in blocks if bid.lower() == block_id.lower()]
        if not blocks_to_test:
            print(f"Error: Block '{block_id}' not found in {markdown_file}")
            print(f"Available blocks: {', '.join([b[0] for b in blocks])}")
            sys.exit(1)
    
    # Test the blocks
    lexer = VerseLexer()
    
    for block_id, code in blocks_to_test:
        print(f"\n{'='*70}")
        print(f"CODE BLOCK #{block_id}")
        print(f"{'='*70}")
        print(code[:200] + ('...' if len(code) > 200 else ''))
        print(f"\n{'-'*70}")
        print("TOKEN ANALYSIS (first 30 tokens):")
        print(f"{'-'*70}")
        
        try:
            tokens = list(lex(code, lexer))
            
            # Show first 30 tokens to avoid overwhelming output
            for token_type, value in tokens[:30]:
                if value.strip():  # Skip pure whitespace
                    token_name = str(token_type).replace('Token.', '')
                    print(f"{token_name:35} | {repr(value[:50])}")
            
            if len(tokens) > 30:
                print(f"\n... and {len(tokens) - 30} more tokens")
        except Exception as e:
            print(f"ERROR: {e}")
    
    print(f"\n{'='*70}")
    print(f"Tested {len(blocks_to_test)} block(s)")
    print(f"{'='*70}")


if __name__ == '__main__':
    main()

