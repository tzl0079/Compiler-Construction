import argparse
from lexer import Lexer, TOKEN_TYPES
import gzip


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

    # Validating gzip file is used
    if file.endswith('.gz'):
        # Ensuring the gzip file is valid
        try:
            with gzip.open(file, 'rt') as f:
                text = f.read()
        # If invalid, print an error and return the file
        except (OSError, gzip.BadGzipFile) as e:
            print(f"Error:The file '{file} is not a valid gzip file. {str(e)}")
            return file, None
        
    # Reading other files
    else:
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
    parser = argparse.ArgumentParser(description='Process a gzip file through the lexer.')
    # Adding the 'files' argument
    parser.add_argument('files', nargs='+', type=str, help='The file to be processed.')
    # Adding the 'list-tokens' argument
    parser.add_argument('-L', '--list-tokens', action='store_true', help='Print the list of tokens.')
    
    # Parse the above added arguments
    args = parser.parse_args()

    read_file(args.file)

