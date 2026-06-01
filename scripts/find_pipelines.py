import ast
import sys

def is_pipeline_file(filename):
    # Αποκλείουμε το ίδιο το script για να μην το επιλέγει
    if 'find_pipelines.py' in filename:
        return False
        
    try:
        with open(filename, "r") as f:
            content = f.read()
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    for decorator in node.decorator_list:
                        # Έλεγχος για @dsl.pipeline ή @pipeline
                        is_dsl = (isinstance(decorator, ast.Attribute) and decorator.attr == 'pipeline')
                        is_name = (isinstance(decorator, ast.Name) and decorator.id == 'pipeline')
                        
                        # Έλεγχος για @kfp.dsl.pipeline(name=...) -> ast.Call
                        is_call = (isinstance(decorator, ast.Call) and 
                                  ((isinstance(decorator.func, ast.Attribute) and decorator.func.attr == 'pipeline') or 
                                   (isinstance(decorator.func, ast.Name) and decorator.func.id == 'pipeline')))
                        
                        if is_dsl or is_name or is_call:
                            print(f"DEBUG: Pipeline decorator found in {filename}", file=sys.stderr)
                            return True
    except Exception as e:
        print(f"DEBUG: Error in {filename}: {e}", file=sys.stderr)
    return False

if __name__ == "__main__":
    changed_files = sys.argv[1:]
    # Φιλτράρουμε μόνο αρχεία που υπάρχουν και είναι .py
    pipeline_files = [f for f in changed_files if f.endswith(".py") and is_pipeline_file(f)]
    print(" ".join(pipeline_files))