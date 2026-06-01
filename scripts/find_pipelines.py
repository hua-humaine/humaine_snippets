import ast
import sys

def is_pipeline_file(filename):
    if 'find_pipelines.py' in filename:
        return False
    try:
        with open(filename, "r") as f:
            tree = ast.parse(f.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    for decorator in node.decorator_list:
                        # DEBUG: Εκτύπωσε τον τύπο του decorator που βρίσκει
                        print(f"DEBUG: Checking {filename} - Found decorator type: {type(decorator)}", file=sys.stderr)
                        
                        # Αν είναι Call (π.χ. @dsl.pipeline()), τσέκαρε το όνομα της συνάρτησης
                        if isinstance(decorator, ast.Call):
                            func = decorator.func
                            if isinstance(func, ast.Attribute):
                                print(f"DEBUG: Found Call Attribute: {func.attr}", file=sys.stderr)
                                if func.attr == 'pipeline': return True
                            elif isinstance(func, ast.Name):
                                print(f"DEBUG: Found Call Name: {func.id}", file=sys.stderr)
                                if func.id == 'pipeline': return True
                                
                        # Αν είναι Name ή Attribute (π.χ. @pipeline)
                        elif isinstance(decorator, ast.Name):
                            print(f"DEBUG: Found Name: {decorator.id}", file=sys.stderr)
                            if decorator.id == 'pipeline': return True
                        elif isinstance(decorator, ast.Attribute):
                            print(f"DEBUG: Found Attribute: {decorator.attr}", file=sys.stderr)
                            if decorator.attr == 'pipeline': return True
    except Exception as e:
        print(f"DEBUG: Parsing error in {filename}: {e}", file=sys.stderr)
    return False

if __name__ == "__main__":
    changed_files = sys.argv[1:]
    pipeline_files = [f for f in changed_files if f.endswith(".py") and is_pipeline_file(f)]
    print(" ".join(pipeline_files))