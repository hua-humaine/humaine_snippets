import ast
import sys

def is_pipeline_file(filename):
    if 'find_pipelines.py' in filename:
        return False
        
    print(f"  [INFO] Checking file: {filename}...", file=sys.stderr)
    
    try:
        with open(filename, "r") as f:
            content = f.read()
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    for decorator in node.decorator_list:
                        
                        if isinstance(decorator, ast.Call):
                            target = decorator.func
                        else:
                            target = decorator

                        # Checking if it is a pipeline decorator
                        is_attr_pipeline = isinstance(target, ast.Attribute) and target.attr == 'pipeline'
                        is_name_pipeline = isinstance(target, ast.Name) and target.id == 'pipeline'
                        
                        if is_attr_pipeline or is_name_pipeline:
                            
                            print(f"  [SUCCESS] Pipeline found: Function '{node.name}' in {filename}!", file=sys.stderr)
                            return True
                            
    except Exception as e:

        print(f"  [ERROR] Failure reading {filename}: {e}", file=sys.stderr)
        
    return False

if __name__ == "__main__":
    changed_files = sys.argv[1:]
    
    # LOG: Start
    print(f"[START] Searching for pipelines in {len(changed_files)} files that changed...", file=sys.stderr)
    
    pipeline_files = [f for f in changed_files if f.endswith(".py") and is_pipeline_file(f)]
    
    # LOG: Ending
    print(f"[DONE] Searching complete. Found {len(pipeline_files)} files pipeline.", file=sys.stderr)
    
    # Sending results to stdout for .sh script to continue
    print(" ".join(pipeline_files))
