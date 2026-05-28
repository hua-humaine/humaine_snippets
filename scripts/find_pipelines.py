import ast
import sys

def is_pipeline_file(filename):
    """Ελέγχει αν ένα αρχείο περιέχει το @dsl.pipeline decorator."""
    try:
        with open(filename, "r") as f:
            tree = ast.parse(f.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    for decorator in node.decorator_list:
                        if (isinstance(decorator, ast.Attribute) and decorator.attr == 'pipeline') or \
                           (isinstance(decorator, ast.Name) and decorator.id == 'pipeline'):
                            return True
    except:
        pass
    return False

if __name__ == "__main__":
    # Παίρνει τα ονόματα των αρχείων από τα command line arguments
    changed_files = sys.argv[1:]
    
    # Φιλτράρει μόνο τα .py αρχεία που όντως έχουν pipeline
    pipeline_files = [f for f in changed_files if f.endswith(".py") and is_pipeline_file(f)]
    
    # Εκτυπώνει τα αρχεία για να τα διαβάσει το bash loop
    print(" ".join(pipeline_files))