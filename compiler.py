# Author: Thomas Lander
# Date: 09/15/24
# compiler.py

import argparse
from lexer import Lexer, TOKEN_TYPES


# Printing tokens (I loved the way Tullis's AI written code printed in code review, so I used the same template)
def print_tokens(tokens):

    # Print the header
    print(f"{'Token':<20} {'Type':<20} {'Line':<5} {'Column':<5}")
    print('-' * 50)

    # Prints each token
    for tokenText, tokenType, line, column in tokens:
        print(f"{repr(tokenText):<20} {tokenType:<20} {line:<5} {column:<5}")


def read_file(file, list_tokens):
    
    text = ""

    # Reading in the file
    if file.endswith('.c'):
        # Ensuring the file is valid
        try:
            with open(file, 'r') as f:
                text = f.read()
        # If invalid, print an error and return the file
        except OSError as e:
            print(f"Error: Could not open file '{file}'. {str(e)}")
            return file, None

    # Sending the text through lexer.py and reading tokens
    lexer = Lexer(TOKEN_TYPES)
    tokens = lexer.tokenize(text)

    # Returns the file and tokens if valid
    if list_tokens:
        return file, tokens
    
    # Just returns the file if not
    return file, None


def main():
    # Setting up the Argument Parser
    parser = argparse.ArgumentParser(description='Process a file through the lexer.')
    # Adding the 'files' argument
    parser.add_argument('files', nargs='+', type=str, help='The file to be processed.')
    # Adding the 'list-tokens' argument
    parser.add_argument('-L', '--list-tokens', action='store_true', help='Print the list of tokens.')
    
    # Parse the above added arguments
    args = parser.parse_args()
    
    # Process each file - ChatGPT helped me write this to deliver before the deadline but nothing is printing in the terminal
    for file in args.files:
        file_path, tokens = read_file(file, list_tokens=args.list_tokens)
        
        # Print the tokens
        if tokens is not None:
            if args.list_tokens:
                print(f"Tokens from file: {file_path}")
                print_tokens(tokens)
            # If flag is not used, just generates
            else:
                print(f"Tokens generated from file: {file_path} but not printed. Use -L to list tokens.")
        else:
            print(f"Failed to process file: {file_path}")


if __name__ == "__compiler__":
    main()