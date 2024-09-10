# Author: Thomas Lander
# Date: 09/10/24
# lexer.py

import re

# Defining token types
TOKEN_TYPES = [
    ('KEYWORD', r'\b(int|double|float|char|return|if|else|while|for)\b'),
    ('IDENTIFIER', r'\b[a-zA-z_][a-zA-Z0-9_]*\b'),
    ('NUMBER', r'\b\d+\b'),
    ('ARTHIMETIC_OPERATOR', r'[+\-*\/]+'),
    ('LOGICAL_OPERATOR', r'[\b(?:and|or|not)\b|&&|\|'),
    ('COMPARISON_OPERATOR', r'[<>]=?|==|!='),
    ('PUNCTUATION', r'[.;]'),
    ('WHITESPACE', r'\s+'),
    ('SINGLE_LINE_COMMENT', r'//[^\n]*'),
    ('MULTI_LINE_COMMENT', r'/\*[\s\S]*?\*/'),
]

class Lexer:
    def __init__(self, rules):

        self.rules = [(re.compile(pattern), token_type) for pattern, token_type in rules]


    def tokenize(self, text):
        tokens = []
        index = 0
        lineNum = 1
        columnNum = 1

        while index < len(text):
            match = None

            # Checking if the new token matches something in the grammar
            for pattern, tokenType in self.rules:
                match = pattern.match(text, index)
                if match:
                    tokenText = match.group(0)
                    tokenLength = len(tokenText)

                    # Adding the new token if it matches
                    tokens.append((tokenText, tokenType, lineNumber, columnNumber))

                    # Updating the index
                    index = match.end(0)

                    # TODO: Calculate the length of the token
          
            # Catching unsupported Grammar
            if not match:
                if index < len(text):
                    charError = text[index]
                else:
                    # End of File reached
                    charError = '<EOF>'

                print(f"Position: {index}, Line number: {lineNum}, Column number: {columnNum}")
                raise SyntaxError(f"Unexpected character: {text[index]} at line {lineNum}, column {columnNum}")
              
    return tokens

