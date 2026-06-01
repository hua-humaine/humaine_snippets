import ast
import sys
import os

def is_pipeline_file(filename):
    # Εδώ τυπώνουμε για να δούμε αν το αρχείο υπάρχει όντως
    if not os.path.exists(filename):
        print(f"DEBUG: File not found: {filename}", file=sys.stderr)
        return False
        
    if 'find_pipelines.py' in filename:
        return False
        
    try:
        with open(filename, "r") as f:
            content = f.read()
            print(f"DEBUG: Reading {filename}...", file=sys.stderr)
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    for decorator in node.decorator_list:
                        # Χαλαρός έλεγχος: αν υπάρχει το όνομα 'pipeline' κάπου στο decorator
                        # Αυτό θα το πιάσει σίγουρα
                        deco_str = ast.dump(decorator)
                        print(f"DEBUG: Found decorator in {filename}: {deco_str}", file=sys.stderr)
                        if 'pipeline' in deco_str:
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