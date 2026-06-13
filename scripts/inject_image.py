import ast
import sys

class KFPImageInjector(ast.NodeTransformer):
    def __init__(self, target_image):
        self.target_image = target_image

    def visit_Call(self, node):
        # Check if decorator is called 'component' ( @dsl.component(...) ή @component(...))
        is_component = False
        if isinstance(node.func, ast.Attribute) and node.func.attr == 'component':
            is_component = True
        elif isinstance(node.func, ast.Name) and node.func.id == 'component':
            is_component = True

        if is_component:
            should_inject = True
            cleaned_keywords = []

            # Check all arguments passed to the decorator
            for kw in node.keywords:
                if kw.arg == 'humaineImage':
                    # If we find 'humaineImage', check if its value is False
                    if isinstance(kw.value, ast.Constant) and kw.value.value is False:
                        should_inject = False
                    # DON'T add it to cleaned_keywords to remove it
                else:
                    # KEEP the remaining arguments normally (e.g., packages_to_install)
                    cleaned_keywords.append(kw)

            if should_inject:
                # 1. Remove 'base_image' or 'target_image' if they are already defined by the dev
                cleaned_keywords = [kw for kw in cleaned_keywords if kw.arg not in ('base_image', 'target_image')]
                
                # 2. Inject our image dynamically!
                cleaned_keywords.append(ast.keyword(
                    arg='base_image', 
                    value=ast.Constant(value=self.target_image)
                ))
            
            # Update the node with the new arguments
            node.keywords = cleaned_keywords

        # Continue the traversal on the rest of the tree
        self.generic_visit(node)
        return node

def main(input_path, output_path, image_url):
    # Read the initial code of the Dev
    with open(input_path, 'r', encoding='utf-8') as f:
        source_code = f.read()

    # Convert it to an AST
    tree = ast.parse(source_code)
    
    # Injection
    transformer = KFPImageInjector(image_url)
    modified_tree = transformer.visit(tree)
    ast.fix_missing_locations(modified_tree)

    # Convert the tree back to Python code
    modified_source = ast.unparse(modified_tree)

    # Save the new, ready-to-use code to the temporary file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(modified_source)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python inject_image.py <input_file> <output_file> <image_url>")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2], sys.argv[3])