# Author: Thomas Lander
# Date: 11/08/24
# my_parser.py 

class Parser: 

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = tokens[0]
        self.symbol_table = SymbolTable()


    # Function to move on to the next token    
    def next(self):
        self.pos += 1
        # Check to see if the token_list is finished
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None
    

    # Function to double check that the token type is correct
    # ChatGPT helped me here with condensing code in a more pythonic way
    def expected_type(self, token_type, token_value = None):
        # Checking if there is a token remaining
        if self.current_token is None:
            raise SyntaxError(f"Unexpected end of input, expected {token_type}")
        # Ensuring the token is correctly identified
        if self.current_token[1] != token_type or (token_value and self.current_token[0] != token_value):
            expected_value = token_value if token_value else token_type
            actual_value = repr(self.current_token[0]) if self.current_token else 'None'
            raise SyntaxError(f"Expected {expected_value}, but got {actual_value} \
                              at line {self.current_token[2]}, column {self.current_token[3]}")
        
        self.next()


    # Main parsing function
    def parse(self):
        ast = []

        # Start parsing - declarations, functions, etc.
        while self.current_token is not None:
            if self.current_token and self.current_token[1] == 'KEYWORD':
                ast.append(self.parse_function_definition())
            else:
                ast.append(self.parse_statement())
    
        return ast


    # Function Definitions Parsing - "int main()" and such
    def parse_function_definition(self):
        if self.current_token[1] == 'KEYWORD': 
            return_type = self.current_token[0]
            self.next()
        else:
            raise SyntaxError(f"Expected return type (KEYWORD), but got {self.current_token[1]}")

        function_name = self.current_token[0]
        self.expected_type('IDENTIFIER') 

        # Add to the Symbol Table and enter a new scope
        self.symbol_table.define_function(function_name, return_type)
        self.symbol_table.enter_scope()

        # Parsing Parameters within parentheses
        self.expected_type('PUNCTUATION', '(')
        parameters = self.parse_parameters()
        # Add the parameters to symbol table
        for param_type, param_name in parameters:
            self.symbol_table.declare_variable(param_name, param_type)
        self.expected_type('PUNCTUATION', ')')

        body = self.parse_block(enter_scope = False)
        self.symbol_table.exit_scope()

        return ('FunctionDefinition', return_type, function_name, parameters, body)
    

    # Helper Function for Function Definition Parsing  
    def parse_parameters(self):
        parameters = []

        # While there are parameters, identify what they are
        while self.current_token and self.current_token[1] in ['KEYWORD', 'IDENTIFIER']:
            param_type = self.current_token[0]
            self.expected_type('KEYWORD') 

            param_name = self.current_token[0]
            self.expected_type('IDENTIFIER')

            parameters.append((param_type, param_name))

            if self.current_token[0] == ',':
                self.expected_type('PUNCTUATION')

        return parameters
    

    # Parsing Function Calls
    def parse_function_call(self):
        function_name = self.current_token[0]

        self.expected_type('IDENTIFIER')
        self.expected_type('PUNCTUATION', '(')

        arguments = []

        # Parsing everything between paranthesis 
        if self.current_token and self.current_token[0] != ')':
            while True:
                arguments.append(self.parse_expression())
                if self.current_token[0] == ')':
                    break
                self.expected_type('PUNCTUATION', ',')

        self.expected_type('PUNCTUATION', ')')
        return ('FunctionCall', function_name, arguments)


    # Declaration Parsing - "int x"
    def parse_declaration(self):
        # Obtaining variable type
        var_type = self.current_token[0]
        self.next()
        
        if self.current_token[1] == 'IDENTIFIER':
            var_name = self.current_token[0]
            # Only declare the variable in the current (function) scope if it doesn’t already exist
            if not self.symbol_table.lookup(var_name, current_scope_only=True):
                self.symbol_table.declare_variable(var_name, var_type)
            self.next()
        else:
            raise SyntaxError(f"Expected IDENTIFIER, but got {self.current_token}")

        # Double checking for additional assignments 
        assignment = None
        if self.current_token[1] == 'ASSIGNMENT_OPERATOR':
            # Skipping "=" and then parsing
            self.next()
            assignment = self.parse_expression()

        self.expected_type('PUNCTUATION', ';')

        # Returning the declaration depending on if a value was assigned
        return ('Declaration', var_type, var_name, assignment) if assignment else ('Declaration', var_type, var_name)


    # Assignment Parsing - "x = 10"
    def parse_assignment(self):
        var_name = self.current_token[0]
        
        # Checking Symbol Table for prior variable declaration
        if self.symbol_table.lookup(var_name):
            self.next()
        else:
            raise NameError(f"Variable '{var_name}' not declared.")
        
        self.expected_type('ASSIGNMENT_OPERATOR', '=')
        expression = self.parse_expression()
        self.expected_type('PUNCTUATION', ';')

        return ('Assignment', var_name, expression)


    # Statement Parsing
    def parse_statement(self):
        # If no more tokens exist, stop parsing
        if self.current_token is None:
            raise SyntaxError("Unexpected end of input")
        
        # Takes in Keywords and Identifiers, error elsewise
        if self.current_token[1] == 'KEYWORD':
            if self.current_token[0] == 'if':
                return self.parse_if_statement()
            elif self.current_token[0] == 'while':
                return self.parse_while_loop()
            elif self.current_token[0] == 'for':
                return self.parse_for_loop()
            elif self.current_token[0] in ['int', 'float']:
                return self.parse_declaration()
            elif self.current_token[0] == 'return':
                return self.parse_return_statement()
        elif self.current_token[1] == 'IDENTIFIER':
            # Look ahead to identify if this is an assignemnt or unary operation
            if self.pos + 1 < len(self.tokens) and self.tokens[self.pos + 1][1] in {'ASSIGNMENT_OPERATOR', 'INCREMENT_OPERATOR', 'DECREMENT_OPERATOR'}:
                # Basic assignment
                if self.tokens[self.pos + 1][1] == 'ASSIGNMENT_OPERATOR':
                    return self.parse_assignment()
                # Handling post-increment/decrement
                elif self.tokens[self.pos + 1][1] in {'INCREMENT_OPERATOR', 'DECREMENT_OPERATOR'}:
                    var_name = self.current_token[0]
                    self.next()  
                    op_token = self.current_token
                    self.next()  
                    self.expected_type('PUNCTUATION', ';')
                    return ('UnaryExpression', op_token[0], ('Variable', var_name))
        # Handling pre-increment/decrement
        elif self.current_token[1] in {'INCREMENT_OPERATOR', 'DECREMENT_OPERATOR'}:
            op_token = self.current_token
            self.next()  
            var_name = self.current_token[0]
            self.expected_type('IDENTIFIER')
            self.expected_type('PUNCTUATION', ';')
            return ('UnaryExpression', op_token[0], ('Variable', var_name))
        else:
            raise SyntaxError(f"Unexpected token: {self.current_token}")
        

    # If-Statement Parsing: if (condition) {statements} 
    def parse_if_statement(self):
        self.next()

        self.expected_type('PUNCTUATION', '(')
        condition = self.parse_expression() 
        self.expected_type('PUNCTUATION', ')') 

        block = self.parse_block()
        else_block = None

        # Handling else statement
        if self.current_token and self.current_token[0] == 'else':
            self.next() 
            else_block = self.parse_block()

        return ('IfStatement', condition, block, else_block)
    

    # While-loop Parsing: while (condition) {statements}
    # ChatGPT helped me debug the random NONE node added
    def parse_while_loop(self):
        self.next()
        self.expected_type('PUNCTUATION', '(')

        condition = self.parse_expression()
        self.expected_type('PUNCTUATION', ')') 
        
        # Check if the body/statements is longer than one line
        if self.current_token and self.current_token[0] == '{':
            body = self.parse_block() 
        else:
            single_statement = self.parse_statement()
            body = [single_statement] if single_statement else []

        return ('WhileLoop', condition, body)
    

    # For-loop Parsing: for (initilization; condition; update) {statements})
    def parse_for_loop(self):
        # Skip 'for ('
        self.next()  
        self.expected_type('PUNCTUATION', '(')

        # Initialization (can be a declaration or an assignment)
        initialization = None
        if self.current_token and self.current_token[0] != ';':
            if self.current_token[1] == 'KEYWORD': 
                initialization = self.parse_declaration()
            else: 
                initialization = self.parse_assignment()
        if self.current_token and self.current_token[0] == ';':
            self.next()

        # Conditional Statement
        condition = None
        if self.current_token and self.current_token[0] != ';':
            condition = self.parse_expression()
            self.next()

        # Update Statement (expression, e.g., i++)
        update = None
        if self.current_token and self.current_token[0] != ')':
            update = self.parse_expression()

        if self.current_token and self.current_token[0] == ')':
            self.next()

        # Body
        if self.current_token and self.current_token[0] == '{':
            self.symbol_table.enter_scope()
            body = self.parse_block()
        else:
            body = [self.parse_statement()]
            self.symbol_table.exit_scope()
        self.symbol_table.exit_scope()

        return ('ForLoop', initialization, condition, update, body)

    
    # Parsing return statements
    def parse_return_statement(self):
        self.next()
    
        # Handling optional expression
        return_value = None
        if self.current_token and self.current_token[0] != ';':
            return_value = self.parse_expression()
    
        self.expected_type('PUNCTUATION', ';')
    
        return ('ReturnStatement', return_value)
    

    # Helper function to parse through Block Statements
    def parse_block(self, enter_scope = True):
        # Enter a new scope, if needed
        if enter_scope:
            self.symbol_table.enter_scope()

        self.expected_type('PUNCTUATION', '{')
        statements = []

        # Everything within brackets is considered inside the block
        while self.current_token and self.current_token[0] != '}':
            statement = self.parse_statement()
            if statement is not None:
                 statements.append(statement)  

        self.expected_type('PUNCTUATION', '}')
        # Exit the scope if entered
        if enter_scope:
            self.symbol_table.exit_scope()

        return ('Block', statements)


    # Expression Parsing - ChatGPT helped me fill in some gaps here, mostly with helper functions
    def parse_expression(self, priority = 0):
        # Check for pre-increment or pre-decrement
        if self.current_token[0] in ('++', '--'):
            op_token = self.current_token
            self.next()  
            operand = self.parse_primaryExp() 
            return ('UnaryExpression', op_token[0], operand)

        # If the expression is ID + '=', treat it as an assignment
        if self.current_token[1] == 'IDENTIFIER' and self.pos + 1 < len(self.tokens) \
                            and self.tokens[self.pos + 1][1] == 'ASSIGNMENT_OPERATOR':
            var_name = self.current_token[0]
            self.next()  
            self.expected_type('ASSIGNMENT_OPERATOR', '=')
            value_expr = self.parse_expression(priority)  
            return ('Assignment', var_name, value_expr)
    
        # Handle non-assignment expressions
        left_expr = self.parse_primaryExp()

        # While the next token is an operator, parse the binary operation
        while self.current_token and self.is_operator(self.current_token) and \
                            self.get_priority(self.current_token) > priority:
            op_token = self.current_token
            self.next()
            right_expr = self.parse_expression(self.get_priority(op_token))
            left_expr = ('BinaryExpression', op_token[0], left_expr, right_expr)

        return left_expr
    

    # Helper function for Expression Parsing in order to parse a primary expression
    # (literal, identifer, or an expression in paratheses)
    def parse_primaryExp(self):
        token = self.current_token

        # Takes in numeric literals (int, float, hex, binary, octal) 
        if token[1] in {'INTEGER_LITERAL', 'FLOATING_POINT_LIT', 'HEX_LITERAL', 'BINARY_LITERAL', 'OCTAL_LITERAL'}:
            self.next()
            # Determine the correct numeric type based on the token type
            value_str = token[0]
            token_type = token[1]
            if token_type in 'INTEGER_LITERAL':
                value = int(value_str)
            elif token_type == 'FLOATING_POINT_LIT':
                value = float(value_str)
            elif token_type == 'HEX_LITERAL':
                value = int(value_str, 16)
            elif token_type == 'BINARY_LITERAL':
                value = int(value_str, 2)
            elif token_type == 'OCTAL_LITERAL':
                value = int(value_str, 8)
            else:
                raise ValueError(f"Unknown numeric literal type: {token_type}")
            return ('Number', value)
        
        elif token[1] == 'IDENTIFIER':
            self.next()
            # Check for postfix increment or decrement
            if self.current_token and self.current_token[0] in ('++', '--'):
                op_token = self.current_token
                self.next()  
                return ('UnaryExpression', op_token[0], ('Variable', token[0]), 'postfix')

            if self.symbol_table.lookup(token[0]):
                return ('Variable', token[0])
            else:
                raise NameError(f"Variable '{token[0]}' not declared.")
        elif token[1] == 'STRING_LITERAL':  
            self.next()
            return ('StringLiteral', token[0])
        elif token[0] == '(':
            self.next()
            # Recursively call parse_expression to handle the expression within 
            expr = self.parse_expression()
            self.expected_type('PUNCTUATION', ')')
            return expr
        else:
            raise SyntaxError(f"Unexpected token: {token}")


    # Helper function for Expression Parsing to check if a token is an operator
    def is_operator(self, token):
        return token[1] == "ARITHMETIC_OPERATOR" or "LOGICAL_OPERATOR"


    # Helper function to ensure correct order of arthimetic operations
    # AI helped me with the use of a precendence/priority table
    def get_priority(self, token):
        priority_map = {
            '||': 1,  # Logical OR
            '&&': 2,  # Logical AND
            '==': 3, '!=': 3,  # Comparison operators
            '<': 4, '>': 4, '<=': 4, '>=': 4,   # More comparison operators
            '+': 5, '-': 5,  # Addition and subtraction
            '*': 6, '/': 6, '%': 6,  # Multiplication, division, and modulus 
        }
        return priority_map.get(token[0], 0)


class SymbolTable:
    def __init__(self):
        self.scopes = [{}]  
        # Tracking exited scopes
        self.exited_scopes = []

    # Entering a new scope
    def enter_scope(self):
        self.scopes.append({})

    # Exiting a scope
    def exit_scope(self):
        if not self.scopes:
            raise IndexError("No scope to exit")
        exited_scope = self.scopes.pop()
        self.exited_scopes.append(exited_scope)
        return exited_scope

    # Declaring variables in the Symbol Table
    def declare_variable(self, name, var_type):
        if not self.scopes:
            raise IndexError("No scope available for declaration")
        if name in self.scopes[-1]:
            raise NameError(f"Variable '{name}' already declared in this scope.")
        self.scopes[-1][name] = var_type

    # Checking for if variables already exist
    def lookup(self, name, current_scope_only = False):
        if current_scope_only:
            return self.scopes[-1].get(name)
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    # Check if function already exists
    def define_function(self, name, return_type):
        if name in self.scopes[0]:
            raise NameError(f"Function '{name}' already declared.")
        self.scopes[0][name] = return_type