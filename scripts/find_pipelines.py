import ast
import sys
import os

def is_pipeline_file(filename):
    if 'find_pipelines.py' in filename:
        return False
    try:
        with open(filename, "r") as f:
            content = f.read()
            tree = ast.parse(content)
            
            # Ψάχνουμε όλους τους κόμβους για να δούμε τι υπάρχει
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    print(f"DEBUG: Found function '{node.name}' in {filename}", file=sys.stderr)
                    for decorator in node.decorator_list:
                        deco_dump = ast.dump(decorator)
                        print(f"DEBUG: Found decorator: {deco_dump}", file=sys.stderr)
                        # Αν υπάρχει η λέξη 'pipeline' οπουδήποτε, το δεχόμαστε!
                        if 'pipeline' in deco_dump.lower():
                            return True
    except Exception as e:
        print(f"DEBUG: Error parsing {filename}: {e}", file=sys.stderr)
    return False

if __name__ == "__main__":
    # Debug: Δες τι ακριβώς έλαβε το script
    print(f"DEBUG: Arguments received: {sys.argv[1:]}", file=sys.stderr)
    
    changed_files = sys.argv[1:]
    pipeline_files = [f for f in changed_files if f.endswith(".py") and is_pipeline_file(f)]
    
    # Εκτύπωση αποτελέσματος
    print(" ".join(pipeline_files))