# Author: Thomas Lander
# Date: 11/08/24
# optimize.py 


# Add optimization for the actual 3ac

class NodeOptimizer:
    def __init__(self, ast):
        self.ast = ast
        self.constant_values = {}

    def optimize(self, constant_folding = False, constant_propagation = False, dead_code_elimination = False):
        # Apply optimization techniques based on flags
        if constant_folding:
            self.ast = [self.constant_folding(node) for node in self.ast]
        if constant_propagation:
            self.ast = [self.propagate_constants(node) for node in self.ast]
        if dead_code_elimination:
            self.ast = [self.remove_dead_code(node) for node in self.ast]
        
        return self.ast


    # Constant folding for binary expressions and direct numeric computations
    def constant_folding(self, node):
        node_type = node[0]

        if node_type == 'BinaryExpression':
            _, operator, left, right = node
            # Recursively simplify left and right expressions
            left = self.constant_folding(left)
            right = self.constant_folding(right)
    
            # Check if both sides are now constants after folding
            if left[0] == 'Number' and right[0] == 'Number':
                result = self.evaluate_exp(operator, float(left[1]), float(right[1]))
                return ('Number', str(result))  # Return a simplified constant expression
            else:
                return ('BinaryExpression', operator, left, right)

        elif node_type == 'UnaryExpression':
            _, operator, operand = node
            operand = self.constant_folding(operand)
            if operand[0] == 'Number':
                # Handle unary operations on constants
                if operator == '++':
                    return ('Number', str(int(operand[1]) + 1))
                elif operator == '--':
                    return ('Number', str(int(operand[1]) - 1))
            return ('UnaryExpression', operator, operand)

        elif node_type == 'IfStatement':
            _, condition, if_block, else_block = node
            optimized_condition = self.constant_folding(condition)
            if optimized_condition[0] == 'Number':
                # Simplify if condition is a constant
                if optimized_condition[1] == '1':
                    return self.constant_folding(if_block)
                elif optimized_condition[1] == '0':
                    return self.constant_folding(else_block) if else_block else None
            else:
                # Recursively fold both branches
                optimized_if_block = [self.constant_folding(stmt) for stmt in if_block]
                optimized_else_block = [self.constant_folding(stmt) for stmt in else_block] if else_block else None
                return ('IfStatement', optimized_condition, optimized_if_block, optimized_else_block)

        elif node_type == 'ForLoop':
            _, init, condition, update, body = node
            optimized_init = self.constant_folding(init) if init else None
            optimized_condition = self.constant_folding(condition) if condition else None
            optimized_update = self.constant_folding(update) if update else None
            optimized_body = [self.constant_folding(stmt) for stmt in body]
            return ('ForLoop', optimized_init, optimized_condition, optimized_update, optimized_body)

        elif node_type == 'ReturnStatement':
            _, value = node
            return ('ReturnStatement', self.constant_folding(value))

        # Process function blocks and any nested statements
        elif node_type == 'Block':
            return ('Block', [self.constant_folding(stmt) for stmt in node[1]])

        # Return other types as-is (Number, Variable, etc.)
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
            return left / right 
        elif operator == '%':
            return left % right
        else:
            raise ValueError(f"Unknown operator: {operator}")


    # Constant propagation for declarations and assignments
    # ChatGPT has been helping me debug, not to much avail however
    def propagate_constants(self, node):
        node_type = node[0]

        # Check if Declaration and if it is of the form "int x = 5"
        # Node Structure - ('Declaration', var_type, var_name, assignment)
        #               OR ('Declaration', var_type, var_name)
        if node_type == 'Declaration' and len(node) == 4:
            _, var_type, var_name, value = node
            value = self.constant_folding(value)  
            # If value exists and is a number
            if value and value[0] == 'Number':
                # Store the constant 
                self.constant_values[var_name] = value[1]
            return node
        
        # Node Structure - ('Assignment', var_name, expression)
        elif node_type == 'Assignment':
            _, var_name, value = node
            evaluated_value = self.constant_folding(value)
            if evaluated_value[0] == 'Number':
                self.constant_values[var_name] = evaluated_value[1]
            elif var_name in self.constant_values:
                # Remove if no longer a constant
                del self.constant_values[var_name] 
            return ('Assignment', var_name, evaluated_value)

        elif node_type == 'Variable':
            var_name = node[1]
            if var_name in self.constant_values:
                return ('Number', self.constant_values[var_name])
            return node
        
        # Recursively handle BinaryExpression, UnaryExpression, IfStatement, ForLoop, WhileLoop, Block, etc.
        elif node_type in {'BinaryExpression', 'UnaryExpression', 'IfStatement', 'ForLoop', 'WhileLoop', 'Block', 'ReturnStatement'}:
            return self.constant_folding(node)

        # Recursively handle other nodes that may contain expressions
        elif isinstance(node[1:], tuple):
            return (node[0], *[self.propagate_constants(child) if isinstance(child, tuple) else child for child in node[1:]])
        
        # Return just the node if unapplicable for propagation
        return node

    # Removing Dead Code
    def remove_dead_code(self, ast):
        used_vars = set()
        cleaned_ast = []
        
        # Step 1: Collect all used variables in the AST
        for node in ast:
            self.collect_used_variables(node, used_vars)
        #print(f"Used variables after collection: {used_vars}") 

        # Step 2: Filter out declarations and assignments for unused variables
        for node in ast:
            node_type = node[0]
            # Node Structure - ('Declaration', var_type, var_name, assignment)
            #               OR ('Declaration', var_type, var_name)
            if node_type == 'Declaration':
                var_name = node[2]
                if var_name in used_vars:
                    cleaned_ast.append(node)
                    #(f"Keeping used variable declaration: {var_name}")
                else:
                    #print(f"Removing unused variable declaration: {var_name}")  # Debug statement
                    continue
 
            else:
                # For other nodes (like ReturnStatement), keep them as they are.
                cleaned_ast.append(node)

        return cleaned_ast

    # Helper method for dead code
    def collect_used_variables(self, node, used_vars):
        #Recursively traverse the AST to collect all variables that are actually used.
        if isinstance(node, tuple):
            node_type = node[0]

            if node_type == 'Variable':
                # Collect variable if it’s used in any expression
                used_vars.add(node[1])

            # Node Structure - ('Declaration', var_type, var_name, assignment)
            #               OR ('Declaration', var_type, var_name)
            elif node_type == 'Declaration':
                # Only add the declared variable if it's assigned a value
                if len(node) > 3 and node[3] is not None:
                    used_vars.add(node[2]) 
                    self.collect_used_variables(node[3], used_vars)

            # Traverse child nodes in expressions, assignments, control structures, etc.
            for child in node[1:]:
                if isinstance(child, tuple):
                    self.collect_used_variables(child, used_vars)
                elif isinstance(child, list):
                    for item in child:
                        self.collect_used_variables(item, used_vars)
    

# Example usage:
# optimizer = Optimizer(ast)
# optimized_ast = optimizer.optimize()