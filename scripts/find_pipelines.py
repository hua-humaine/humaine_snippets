import ast
import sys

def is_pipeline_file(filename):
    """Ελέγχει αν ένα αρχείο περιέχει το @dsl.pipeline decorator."""
    try:
        with open(filename, "r") as f:
            content = f.read()
            # Debug: Εκτύπωσε στο stderr για να μην επηρεάζει το print του stdout
            if '@pipeline' in content or 'dsl.pipeline' in content:
                print(f"DEBUG: Found potential pipeline in {filename}", file=sys.stderr)
            
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    for decorator in node.decorator_list:
                        # Εδώ βλέπουμε αν είναι Name, Attribute ή Call
                        # Συχνά είναι @dsl.pipeline(...) που είναι ast.Call
                        if isinstance(decorator, ast.Name) and decorator.id == 'pipeline':
                            return True
                        if isinstance(decorator, ast.Attribute) and decorator.attr == 'pipeline':
                            return True
                        if isinstance(decorator, ast.Call):
                            # Αν το decorator είναι κλήση (π.χ. @dsl.pipeline(name='...'))
                            if isinstance(decorator.func, ast.Attribute) and decorator.func.attr == 'pipeline':
                                return True
                            if isinstance(decorator.func, ast.Name) and decorator.func.id == 'pipeline':
                                return True
    except Exception as e:
        print(f"DEBUG: Error parsing {filename}: {e}", file=sys.stderr)
    return False

if __name__ == "__main__":
    # Παίρνει τα ονόματα των αρχείων από τα command line arguments
    changed_files = sys.argv[1:]
    
    # Φιλτράρει μόνο τα .py αρχεία που όντως έχουν pipeline
    pipeline_files = [f for f in changed_files if f.endswith(".py") and is_pipeline_file(f)]
    
    # Εκτυπώνει τα αρχεία για να τα διαβάσει το bash loop
    print(" ".join(pipeline_files))