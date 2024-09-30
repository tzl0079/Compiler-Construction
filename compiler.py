# Author: Thomas Lander
# Date: 09/15/24
# compiler.py

import argparse
from lexer import Lexer, TOKEN_TYPES
from my_parser import Parser


# Printing tokens (I loved the way Tullis's AI written code printed in code review, so I used the same template)
def print_tokens(tokens):

    # Print the header
    print(f"{'Token':<20} {'Type':<20} {'Line':<5} {'Column':<5}")
    print('-' * 50)

    # Prints each token
    for tokenText, tokenType, line, column in tokens:
        print(f"{repr(tokenText):<20} {tokenType:<20} {line:<5} {column:<5}")


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
            parser = Parser(tokens)  # Initialize the parser with tokens
            ast = parser.parse()  # Generate the AST
            
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