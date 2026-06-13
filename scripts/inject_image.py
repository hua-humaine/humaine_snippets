import ast
import sys

class KFPImageInjector(ast.NodeTransformer):
    """
    AST Transformer to inject or update the 'base_image' argument 
    in Kubeflow Pipelines (KFP) v2 @component decorators.
    """
    def __init__(self, target_image):
        self.target_image = target_image

    def visit_Call(self, node):
        """
        Visits function calls to identify KFP @component decorators 
        and modify their keyword arguments.
        """
        # Identify if the call is a @component decorator
        is_component = (isinstance(node.func, ast.Attribute) and node.func.attr == 'component') or \
                       (isinstance(node.func, ast.Name) and node.func.id == 'component')
        
        if is_component:
            should_inject = True
            new_keywords = []

            # Process existing keyword arguments
            for kw in node.keywords:
                if kw.arg == 'humaineImage':
                    # If humaineImage flag is explicitly False, skip injection
                    if isinstance(kw.value, ast.Constant) and kw.value.value is False:
                        should_inject = False
                    # Remove 'humaineImage' from the final arguments list
                elif kw.arg in ('base_image', 'target_image'):
                    # Skip existing base_image to avoid duplicates
                    continue
                else:
                    new_keywords.append(kw)

            # Inject the new base_image if allowed
            if should_inject:
                print(f"[DEBUG] Injecting base_image={self.target_image}")
                new_keywords.append(ast.keyword(
                    arg='base_image', 
                    value=ast.Constant(value=self.target_image)
                ))
            
            # Apply modified keyword list back to the node
            node.keywords = new_keywords

        # Continue traversing the AST
        self.generic_visit(node)
        return node

def main(input_path, output_path, image_url):
    """
    Parses the pipeline source code, performs AST transformation, 
    and saves the modified code to the output path.
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        source_code = f.read()

    # Parse the source code into an Abstract Syntax Tree (AST)
    tree = ast.parse(source_code)
    
    # Perform the AST transformation
    transformer = KFPImageInjector(image_url)
    modified_tree = transformer.visit(tree)
    
    # Fix line numbers and column offsets
    ast.fix_missing_locations(modified_tree)

    # Unparse the tree back into source code string
    modified_source = ast.unparse(modified_tree)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(modified_source)

if __name__ == "__main__":
    # Ensure correct number of arguments provided
    if len(sys.argv) < 4:
        print("Usage: python inject_image.py <input_file> <output_file> <image_url>")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2], sys.argv[3])