# Author: Thomas Lander
# Date: 10/31/24
# optimize.py 

class Optimizer:
    def __init__(self, ast):
        self.ast = ast

    def optimize(self):
        # Apply constant folding and constant propagation for right now.
        # In the future with more optimization techniques I will add the 
        # ability to choose which passes you want, with flags
        self.constant_values = {}  
        optimized_ast = [self.check_node(node) for node in self.ast]
        return optimized_ast

    # Entry method to check each node and apply optimizations
    def check_node(self, node):
        node_type = node[0]
        if node_type == 'BinaryExpression':
            return self.fold_constants(node)
        elif node_type == 'Declaration':
            return self.propagate_constant(node)
        elif node_type == 'Assignment':
            return self.propagate_constant(node)
        elif node_type == 'WhileLoop':
            _, condition, body = node
            optimized_condition = self.check_node(condition)
            optimized_body = [self.check_node(stmt) for stmt in body]
            return ('WhileLoop', optimized_condition, optimized_body)
        elif node_type in {'Number', 'Variable', 'StringLiteral'}:
            return node
        else:
            # Recursively process any child nodes for other types
            return tuple(self.check_node(child) if isinstance(child, tuple) else child for child in node)

    # Constant folding for binary expressions
    def fold_constants(self, node):
        _, operator, left, right = node
        left = self.check_node(left)
        right = self.check_node(right)
        
        if left[0] == 'Number' and right[0] == 'Number':
            # If both sides are constants, do folding
            result = self.evaluate_exp(operator, int(left[1]), int(right[1]))
            return ('Number', str(result))
        else:
            # Return the original expression if we can't fold
            return ('BinaryExpression', operator, left, right)

    # Constant propagation for declarations and assignments
    def propagate_constant(self, node):
        # Check if Declaration and if it is of the form "int x = 5"
        if node[0] == 'Declaration' and len(node) == 4:
            _, var_type, var_name, value = node
            if value and value[0] == 'Number':
                self.constant_values[var_name] = value[1]
            return node

        elif node[0] == 'Assignment':
            _, var_name, value = node
            if value[0] == 'Number':
                self.constant_values[var_name] = value[1]
            else:
                self.constant_values.pop(var_name, None)
            return ('Assignment', var_name, self.check_node(value))

        elif node[0] == 'Variable':
            # Replace with constant if available
            var_name = node[1]
            if var_name in self.constant_values:
                return ('Number', self.constant_values[var_name])
            return node

    # Helper to evaluate expressions during folding
    def evaluate_exp(self, operator, left, right):
        if operator == '+':
            return left + right
        elif operator == '-':
            return left - right
        elif operator == '*':
            return left * right
        elif operator == '/':
            return left // right 
        else:
            raise ValueError(f"Unknown operator: {operator}")

# Example usage:
# optimizer = Optimizer(ast)
# optimized_ast = optimizer.optimize()