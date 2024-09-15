import argparse
from lexer import Lexer, TOKEN_TYPES
import gzip


# Printing tokens (ChatGPT helped me with this to make it pretty)
def print_tokens(tokens):

    # Print the header
    print(f"{'Token':<20} {'Type':<20} {'Line':<5} {'Column':<5}")
    print('-' * 50)

    # Prints each token
    for tokenText, tokenType, line, column in tokens:
        print(f"{repr(tokenText):<20} {tokenType:<20} {line:<5} {column:<5}")


def main():
    pass