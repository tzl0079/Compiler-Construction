# Author: Thomas Lander
# Date: 10/31/24
# compiler.py

import argparse
from lexer import Lexer, TOKEN_TYPES
from my_parser import Parser, SymbolTable
from three_address_code import ThreeAddressCodeGenerator
from optimize import Optimizer


# Printing tokens (I loved the way Tullis's AI written code printed in code review, so I used the same template)
def print_tokens(tokens):

    # Print the header
    print(f"{'Token':<20} {'Type':<20} {'Line':<5} {'Column':<5}")
    print('-' * 50)

    # Prints each token
    for tokenText, tokenType, line, column in tokens:
        print(f"{repr(tokenText):<20} {tokenType:<20} {line:<5} {column:<5}")


# Printing out the AST
def print_ast(node, indent = 0):
    spacing = '  ' * indent

    if isinstance(node, tuple):
        print(f"{spacing}{node[0]}")
        for child in node[1:]:
            print_ast(child, indent + 1)
    elif isinstance(node, list):
        for item in node:
            print_ast(item, indent)
    else:
        print(f"{spacing}{node}")


# Printing out the Symbol Table, having some troubles with it though
def print_symboltable(symbol_table):
    print("Symbol Table:")
    print("--------------------------------------------------")

    # Print Global Scope (function declarations)
    print("Global Scope (function declarations):")
    global_functions = symbol_table.scopes[0]
    for func_name, func_type in global_functions.items():
        print(f"  {func_name}: {func_type}")

    # Print Local Variables in each active and exited scope
    for scope_level, scope in enumerate(symbol_table.scopes[1:], start=1):
        print(f"\nLocal Variables in Active Scope Level {scope_level}:")
        if scope:
            for var_name, var_type in scope.items():
                print(f"  {var_name}: {var_type}")
        else:
            print("  No local variables.")

    for scope_level, scope in enumerate(symbol_table.exited_scopes, start=len(symbol_table.scopes)):
        print(f"\nLocal Variables in Scope Level {scope_level}:")
        if scope:
            for var_name, var_type in scope.items():
                print(f"  {var_name}: {var_type}")
        else:
            print("  No local variables.")


def read_file(file_path):
    # Reading in the file
    with open(file_path, 'r') as file:
        content = file.read()

    lexer = Lexer(TOKEN_TYPES)
    tokens = lexer.tokenize(content)

    return tokens


def main():
    # Setting up the Argument Parser
    parser = argparse.ArgumentParser(description='Process a file through the lexer.')
    parser.add_argument('file', type=str, help='The file to be processed.')
    parser.add_argument('-L', '--list-tokens', action='store_true', help='Print the list of tokens.')
    
    # Parse the above added arguments
    args = parser.parse_args()
    
    file = args.file
    try:
        tokens = read_file(file)
        
        # Print the tokens
        if tokens is not None:
            if args.list_tokens:
                print(f"Tokens from file: {file}")
                print_tokens(tokens)
            # If flag is not used, just generates
            else:
                print(f"Tokens generated from file: {file} but not printed. Use -L to list tokens.")

            # Parse the tokens to generate an AST
            parser = Parser(tokens) 
            ast = parser.parse()

            # Print the AST
            print('-' * 50)
            print("Abstract Syntax Tree:")
            print('-' * 50)
            print_ast(ast)
            print('-' * 50)

            # Print the symbol table
            print_symboltable(parser.symbol_table)

            generator = ThreeAddressCodeGenerator(ast)
            three_point_code = generator.generate()

            print('-' * 50)
            print("3-Address Code:")
            print('-' * 50)
            for line in three_point_code:
                print(line)

        else:
            print(f"Failed to process file: {file}")
    except SyntaxError as e:
        print(f"Syntax error in file '{file}': {e}")
    except FileNotFoundError:
        print(f"Error: File '{file}' not found.")
    except Exception as e:
        print(f"An error occurred while processing '{file}': {e}")


if __name__ == "__main__":
    main()