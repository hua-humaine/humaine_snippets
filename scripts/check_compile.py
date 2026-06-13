import ast
import sys
import os

def has_compile(filepath):
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' not found.", file=sys.stderr)
        return False

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
            
        # Searching nodes
        for node in ast.walk(tree):
            # Check if (Call) exists for a function/method
            if isinstance(node, ast.Call):
                # Check if the function being called is named 'compile'
                if isinstance(node.func, ast.Attribute) and node.func.attr == 'compile':
                    return True
        return False
        
    except SyntaxError as e:
        print(f"Syntax error in '{filepath}': {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Unexpected error parsing '{filepath}': {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_compile.py <path_to_pipeline_file>", file=sys.stderr)
        sys.exit(1)

    filepath = sys.argv[1]
    
    if has_compile(filepath):
        sys.exit(0)  # 0 "Success/True" 
    else:
        sys.exit(1)  # 1 "Error/False"