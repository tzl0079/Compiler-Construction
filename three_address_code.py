# Author: Thomas Lander
# Date: 10/31/24
# three_address_code.py

class ThreeAddressCodeGenerator:
    def __init__(self, ast):
        self.ast = ast
        self.temp_var_count = 0
        self.label_counter = 1
        self.code = []


    # Temporary variables "t1", "t2" to hold expressions
    def new_temp(self):
        self.temp_var_count += 1
        return f"t{self.temp_var_count}"
    

    # Create labels for blocks
    def new_label(self):
        label = f"L{self.label_counter}"
        self.label_counter += 1
        return label


    # Generate 3-Point Code for the given AST
    def generate(self):
        for node in self.ast:
            self.visit(node)
        return self.code


    # Function to handle different node types in the AST
    def visit(self, node):
        node_type = node[0]
        if node_type == 'FunctionDefinition':
            self.visit_function_definition(node)
        elif node_type == 'BinaryExpression':
            return self.visit_binary_expression(node)
        elif node_type == 'IfStatement':
            self.visit_if_statement(node)
        elif node_type == 'WhileLoop':
            self.visit_while_loop(node)
        elif node_type == 'ForLoop':
            self.visit_for_loop(node)
        elif node_type == 'ReturnStatement':
            self.visit_return_statement(node)
        elif node_type == 'Declaration':
            self.visit_declaration(node)
        elif node_type == 'Assignment':
            self.visit_assignment(node)
        elif node_type == 'UnaryExpression':
            self.visit_unary_expression(node)
        elif node_type in {'Number', 'Variable', 'StringLiteral'}:
            return self.visit_primary_expression(node)
        else:
            raise ValueError(f"Unknown node type: {node_type}")


    # Handling function definitions
    # Takes in node - ('FunctionDefinition', return_type, function_name, parameters, body)
    def visit_function_definition(self, node):
        _, return_type, function_name, parameters, body = node
        self.code.append(f"{function_name}() BEGIN")

        # Body that contains Statements
        for statement in body[1]: 
            self.visit(statement)
        self.code.append(f"{function_name}() END")


    # Handling binary expressions (e.g., a + b)
    # Takes in node - ('BinaryExpression', operator, left_expr, right_expr))
    def visit_binary_expression(self, node):
        _, operator, left, right = node
        leftside = self.visit(left)
        rightside = self.visit(right)

        temp_var = self.new_temp()
        self.code.append(f"{temp_var} = {leftside} {operator} {rightside}")

        return temp_var


    # Handling if-statements
    # Takes in node - ('IfStatement', condition, block, temp_block)
    def visit_if_statement(self, node):
        _, condition, true_body, false_body = node
        true_label = self.new_label()
        false_label = self.new_label()
        end_label = self.new_label()

        # Evaluate condition
        condition_temp = self.visit(condition)
        self.code.append(f"if {condition_temp} goto {true_label}")
        self.code.append(f"goto {false_label}")

        # True branch
        self.code.append(f"{true_label}:")
        for stmt in true_body[1]:
            self.visit(stmt)

        # False branch, if exists
        if false_body:
            self.code.append(f"goto {end_label}")
            self.code.append(f"{false_label}:")
            for stmt in false_body[1]:
                self.visit(stmt)
        else:
            self.code.append(f"{false_label}:")

        # End label
        self.code.append(f"{end_label}:")


    # Handling while loops
    # Takes in node - ('WhileLoop', condition, body)
    def visit_while_loop(self, node):
        _, condition, body = node
        start_label = self.new_label()
        body_label = self.new_label()
        end_label = self.new_label()

        # Start of the loop
        self.code.append(f"{start_label}:")

        # Evaluate the conditional statement
        condition_temp = self.visit(condition)
        self.code.append(f"if {condition_temp} goto {body_label}")
        self.code.append(f"goto {end_label}")

        # Loop body
        self.code.append(f"{body_label}:")
        for statement in body:
            self.visit(statement)

        self.code.append(f"goto {start_label}")
        self.code.append(f"{end_label}:")


    # Handling for loops
    # Takes in node - ('ForLoop', initialization, condition, update, body)
    def visit_for_loop(self, node):
        _, initialization, condition, update, body = node
        start_label = self.new_label()
        body_label = self.new_label()
        end_label = self.new_label()

        # Loop initialization
        self.visit(initialization)

        # Start of the loop
        self.code.append(f"{start_label}:")

        # Evaluate the conditional statement
        condition_temp = self.visit(condition)
        self.code.append(f"if {condition_temp} goto {body_label}")
        self.code.append(f"goto {end_label}")

        # Loop body
        self.code.append(f"{body_label}:")
        for statement in body[1]:
            self.visit(statement)

        # Update the 3rd statment
        self.visit(update)

        self.code.append(f"goto {start_label}")
        self.code.append(f"{end_label}:")


    # Handling return statements
    # Takes in node - ('ReturnStatement', return_value)
    def visit_return_statement(self, node):
        _, return_value = node
        if return_value:
            return_temp = self.visit(return_value)
            self.code.append(f"RETURN {return_temp}")
        else:
            self.code.append("RETURN")


    # Handling declarations
    # Takes in node - ('Declaration', var_type, var_name, assignment) 
    #               OR 'Declaration', var_type, var_name) if no assignment
    def visit_declaration(self, node):
        # Declaration w/ initlialization
        if len(node) == 4:
            _, var_type, var_name, initialization = node
            init_value = self.visit(initialization)  # Generate code for initialization
            self.code.append(f"{var_name} = {init_value}")
        # Declaration w/o
        elif len(node) == 3:
            _, var_type, var_name = node
            self.code.append(f"{var_name} = UNINITIALIZED")
        else:
            raise ValueError(f"Unexpected Declaration node format: {node}")
        

    # Handling Assignments
    # Takes in node - ('Assignment', var_name, expression)
    def visit_assignment(self, node):
        _, var_name, expression = node
        expr_value = self.visit(expression)
        self.code.append(f"{var_name} = {expr_value}")


    # Handling Unary Operators
    # Takes in node - ('UnaryExpression', operator, ('Variable', var_name))
    def visit_unary_expression(self, node):
        _, operator, operand, *optional = node
        var_name = self.visit(operand)

        if operator == '++':
            # Post-increment
            if optional and optional[0] == 'postfix':
                # store current value, then increment
                temp_var = self.new_temp()
                self.code.append(f"{temp_var} = {var_name}")
                self.code.append(f"{var_name} = {var_name} + 1")
                return temp_var
            # Pre-increment
            else:
                # increment, then use updated value
                self.code.append(f"{var_name} = {var_name} + 1")
                return var_name
            
        elif operator == '--':
            # Post-decrement
            if optional and optional[0] == 'postfix':
                # store current value, then decrement
                temp_var = self.new_temp()
                self.code.append(f"{temp_var} = {var_name}")
                self.code.append(f"{var_name} = {var_name} - 1")
                return temp_var
            # Pre-decrement
            else:
                # decrement, then use updated value
                self.code.append(f"{var_name} = {var_name} - 1")
                return var_name
        else:
            raise ValueError(f"Unknown unary operator: {operator}")


    # Add support for primary expressions (literals, identifiers, etc.)
    def visit_primary_expression(self, node):
        node_type = node[0]
        # Node types
        if node_type == 'Number':
            return node[1]
        elif node_type == 'Variable':
            return node[1]
        elif node_type == 'StringLiteral':
            temp_var = self.new_temp()
            self.code.append(f'{temp_var} = "{node[1]}"')
            return temp_var
        else:
            raise ValueError(f"Unknown primary expression: {node}")
        
        