# Author: Thomas Lander
# Date: 10/04/24
# my_parser.py 

class Parser: 

    # Initilization Function
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
    # AI helped me here with condensing code in a more pythonic way
    def expected_type(self, token_type, token_value = None):
        # Checking if there is a token remaining
        if self.current_token is None:
            raise SyntaxError(f"Unexpected end of input, expected {token_type}")
        # Ensuring the right token is in the right spot
        if self.current_token[1] != token_type or (token_value and self.current_token[0] != token_value):
            expected_value = token_value if token_value else token_type
            actual_value = repr(self.current_token[0]) if self.current_token else 'None'
            raise SyntaxError(f"Expected {expected_value}, but got {actual_value} at line {self.current_token[2]}, column {self.current_token[3]}")
        
        self.next()


    # Main parsing function
    def parse(self):
        self.symbol_table.enter_scope()
        ast = []

        # Start parsing (e.g., declarations, functions, etc.)
        while self.current_token is not None:
            if self.current_token and self.current_token[1] == 'KEYWORD':
                ast.append(self.parse_function_definition())
            else:
                ast.append(self.parse_statement())

        self.symbol_table.exit_scope()
    
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
        self.expected_type('PUNCTUATION', ')')

        body = self.parse_block()
        self.symbol_table.exit_scope()

        return ('FunctionDefinition', return_type, function_name, parameters, body)
    

    # Helper Function for Function Definition Parsing - 
    # parsing potential parameters in a function definition
    def parse_parameters(self):
        parameters = []

        # Check if there are parameters
        while self.current_token and self.current_token[1] in ['KEYWORD', 'IDENTIFIER']:
            param_type = self.current_token[0]
            self.expected_type('KEYWORD') 

            self.expected_type('IDENTIFIER')
            param_name = self.current_token[0]

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

        if self.current_token and self.current_token[0] != ')':
            while True:
                arguments.append(self.parse_expression())
                if self.current_token[0] == ')':
                    break
                self.expected_type('PUNCTUATION', ',')

        self.expected_type('PUNCTUATION', ')')
        return ('FunctionCall', function_name, arguments)


     # Declaration Parsing
    def parse_declaration(self):
        # Obtaining variable type
        var_type = self.current_token[0]
        self.next()
        
        if self.current_token[1] == 'IDENTIFIER':
            var_name = self.current_token[0]
            # Adding to the Symbol Table
            self.symbol_table.declare(var_name, var_type)
            self.next()
        else:
            raise SyntaxError(f"Expected IDENTIFIER, but got {self.current_token}")

        # Checking for additional assignments
        initialization = None
        if self.current_token[1] == 'ASSIGNMENT_OPERATOR':
            # Skipping "=" and then parsing
            self.next()
            initialization = self.parse_expression()

        self.expected_type('PUNCTUATION', ';')

        if initialization is not None:
            return ('Declaration', var_type, var_name, initialization)
        else:
            return ('Declaration', var_type, var_name)


    # Assignment Parsing 
    def parse_assignment(self):
        var_name = self.current_token[0]
        
        # Checking Symbol Table for prior variable declaration
        if self.symbol_table.lookup(var_name):
            self.next()
        else:
            raise NameError(f"Variable '{var_name}' not declared.")
        
        self.expected_type('ASSIGNMENT_OPERATOR', '=')
        self.parse_expression()
        self.expected_type('PUNCTUATION', ';')


    # Statement Parsing
    def parse_statement(self):
        # Skipping Comments
        if self.current_token[1] in ['SINGLE_LINE_COMMENT', 'MULTI_LINE_COMMENT']:
            self.next()  
            return
        
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
            return self.parse_assignment()
        else:
            raise SyntaxError(f"Unexpected token: {self.current_token}")
        

    # If-Statement Parsing: if (condition) {statements} 
    def parse_if_statement(self):
        self.next()
        self.expected_type('PUNCTUATION', '(')

        condition = self.parse_expression() 

        self.expected_type('PUNCTUATION', ')') 

        block = self.parse_block()
        temp_block = None

        # Handling else statement
        if self.current_token and self.current_token[0] == 'else':
            self.next() 
            temp_block = self.parse_block()

        return ('IfStatement', condition, block, temp_block)
    

    # While-loop Parsing: while (condition) {statements}
    def parse_while_loop(self):
        self.next()
        self.expected_type('PUNCTUATION', '(')

        condition = self.parse_expression()
        self.expected_type('PUNCTUATION', ')') 
        
        # Check if the body/statements is longer than one line
        if self.current_token and self.current_token[0] == '{':
            body = self.parse_block() 
        else:
            body = self.parse_statement()

        return ('WhileLoop', condition, body)
    

    # For-loop Parsing: for (initilization; condition; update) {statements})
    def parse_for_loop(self):
        self.next()
        self.expected_type('PUNCTUATION', '(')

        # Parsing the initialization statement
        initialization = None
        if self.current_token[0] != ';':  
            initialization = self.parse_expression()
        self.expected_type('PUNCTUATION', ';')

        # Parsing the conditional expression
        condition = None
        if self.current_token[0] != ';':
            condition = self.parse_expression()
        self.expected_type('PUNCTUATION', ';')

        # Parsing the update expression
        update = None
        if self.current_token != ')':
            update = self.parse_expression()

        self.expected_type('PUNCTUATION', ')')

        # Checking if the body/statements is longer than 1 line
        if self.current_token and self.current_token[0] == '{':
            body = self.parse_block()  # Parse block if it exists
        else:
            body = self.parse_statement()

        return ('ForLoop', initialization, condition, update, body)
    

    def parse_return_statement(self):
        self.next()
    
        # Handling optional expression
        return_value = None
        if self.current_token and self.current_token[0] != ';':
            return_value = self.parse_expression()
    
        self.expected_type('PUNCTUATION', ';')
    
        return ('ReturnStatement', return_value)
    

    # Helper function to parse through Block Statements
    def parse_block(self):
        # New symbol table scope as we are entering a block
        self.symbol_table.enter_scope()
        self.expected_type('PUNCTUATION', '{')
        statements = []

        while self.current_token and self.current_token[0] != '}':
            statement = self.parse_statement()
            if statement is not None:
                 statements.append(statement)  

        self.expected_type('PUNCTUATION', '}')
        self.symbol_table.exit_scope()

        return ('Block', statements)


    # Expression Parsing - AI helped me fill in some gaps here, mostly with helper functions
    def parse_expression(self, priority = 0):
        leftmost_expr = self.parse_primaryExp()

        # While the next token is an operator, parse the binary operation
        while self.current_token and self.is_operator(self.current_token) and self.get_priority(self.current_token) > priority:
            op_token = self.current_token
            self.next()
            # Look ahead for other operands with higher priority 
            right_expr = self.parse_expression(self.get_priority(op_token))
            leftmost_expr = ('BinaryExpression', op_token[0], leftmost_expr, right_expr)

        return leftmost_expr
    

    # Helper function for Expression Parsing in order to parse a primary expression
    # (literal, identifer, or an expression in paratheses)
    def parse_primaryExp(self):
        token = self.current_token

        # Takes in Integers, Floats, Identifiers, and Parenthetic Operations
        if token[1] == 'INTEGER_LITERAL':
            self.next()
            return ('IntegerLiteral', token[0])
        elif token[1] == 'FLOATING_POINT_LIT':
            self.next()
            return ('FloatingPointLiteral', float(token[0]))
        elif token[1] == 'HEX_LITERAL':  # Handle hex literals
            self.next()
            return ('HexLiteral', token[0])
        elif token[1] == 'BINARY_LITERAL':  # Handle binary literals
            self.next()
            return ('BinaryLiteral', token[0])
        elif token[1] == 'OCTAL_LITERAL':  # Handle octal literals
            self.next()
            return ('OctalLiteral', token[0])
        elif token[1] == 'IDENTIFIER':
            self.next()
            if self.symbol_table.lookup(token[0]):
                return ('Variable', token[0])
            else:
                raise NameError(f"Variable '{token[0]}' not declared.")
        elif token[1] == 'STRING_LITERAL':  # New case for string literals
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

    # Initilization Function
    def __init__(self):
        self.symbols = []
        self.scope_level = -1
        self.function_types = {}
    

    # Function to enter a new scope
    def enter_scope(self):
        self.scope_level += 1
        self.symbols.append({})
        print(f"Entered scope level {self.scope_level}")
    

    # Function to exit the current scope
    def exit_scope(self):
        if self.scope_level > 0:
            local_vars = self.symbols.pop()  # Get local vars before popping
            print(f"Exited scope level {self.scope_level}, local variables: {local_vars}")
            self.scope_level -= 1
    

    # Declaration function
    def declare(self, name, var_type):
        if name in self.function_types:
            raise SyntaxError(f"Function '{name}' already declared.")
        
        if name in self.symbols[self.scope_level]:
            raise SyntaxError(f"Variable '{name}' already declared in the current scope.")
        
        # Store variable or function type
        self.symbols[self.scope_level][name] = var_type
        print(f"Declared {name} of type {var_type} in scope level {self.scope_level}")


    # Defining Functions
    def define_function(self, name, return_type):
        # Make sure it doesn't already exist
        if name in self.function_types:
            raise SyntaxError(f"Function '{name}' already defined.")
        self.function_types[name] = return_type


    # Getting Function Type
    def get_function_type(self, name):
        return self.function_types.get(name, None)
    

    # Lookup function
    def lookup(self, name):
        # Check scopes from innermost to outermost
        for scope in reversed(self.symbols):
            if name in scope:
                return scope[name]
        
        # Returning function type (if found)
        if name in self.function_types:
            return self.function_types[name]

        raise NameError(f"Variable '{name}' not found in any scope.")
    
    
    # Function specifying return type
    def get_function_return_type(self, function_name):
        return self.function_types.get(function_name, None)
    
