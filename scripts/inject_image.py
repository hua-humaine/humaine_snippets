import ast
import sys
import os

# Retrieve KFP version from environment, defaulting to 1 if not specified.
# This allows the script to adapt its injection strategy based on the cluster version.
kfp_version = int(os.environ.get('KFP_VERSION'))
# Στο main()
print(f"[DEBUG] KFP_VERSION detected: {kfp_version}")
class KFPImageInjector(ast.NodeTransformer):
    def __init__(self, target_image, version):
        self.target_image = target_image
        self.version = version

    def visit_Call(self, node):
        is_component = (isinstance(node.func, ast.Attribute) and node.func.attr == 'component') or \
                       (isinstance(node.func, ast.Name) and node.func.id == 'component')
        
        if is_component:
            should_inject = True
            # Use list comprehension to have only the right keywords
            # This is more secure than manually building the list
            node.keywords = [kw for kw in node.keywords if kw.arg not in ('base_image', 'target_image', 'humaineImage')]

            # Check for the humaineImage flag
            for kw in node.keywords:
                pass 
            
            new_keywords = []
            should_inject = True
            
            for kw in node.keywords:
                if kw.arg == 'humaineImage':
                    if isinstance(kw.value, ast.Constant) and kw.value.value is False:
                        should_inject = False
                else:
                    new_keywords.append(kw)
            
            # Injection only if version >= 2
            if should_inject and self.version >= 2:
                print(f"[DEBUG] Injecting base_image={self.target_image}")
                new_keywords.append(ast.keyword(
                    arg='base_image', 
                    value=ast.Constant(value=self.target_image)
                ))
            
            node.keywords = new_keywords
            node._should_inject = should_inject

        self.generic_visit(node)
        return node

    def visit_FunctionDef(self, node):
        """
        Handles post-function definitions, necessary for KFP v1.x compatibility.
        """
        self.generic_visit(node)
        
        # Strategy for KFP v1.x: Use create_component_from_func wrapper instead of decorator
        if self.version < 2:
            # Determine if this function was marked for injection
            should_inject = any(getattr(d, '_should_inject', True) for d in node.decorator_list if hasattr(d, '_should_inject'))
            
            if should_inject:
                # Add the component wrapper assignment after the function definition
                wrapper_node = ast.parse(
                    f"{node.name} = kfp.components.create_component_from_func({node.name}, base_image='{self.target_image}')"
                ).body[0]
                return [node, wrapper_node]
        
        return node

def main(input_path, output_path, image_url):
    """
    Parses, transforms, and saves the modified pipeline source code.
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        source_code = f.read()

    tree = ast.parse(source_code)
    
    # Perform AST transformation
    transformer = KFPImageInjector(image_url, kfp_version)
    modified_tree = transformer.visit(tree)
    ast.fix_missing_locations(modified_tree)

    # Ensure kfp import is present for KFP v1.x dynamic wrapping
    if kfp_version < 2:
        import_node = ast.parse("import kfp").body[0]
        modified_tree.body.insert(0, import_node)

    # Convert back to source code
    modified_source = ast.unparse(modified_tree)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(modified_source)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python inject_image.py <input_file> <output_file> <image_url>")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2], sys.argv[3])