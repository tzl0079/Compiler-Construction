# Author: Thomas Lander
# Date: 09/15/24
# lexer.py

import re

# Credit to these websites for help: https://regexr.com/, 

# My Grammar:
TOKEN_TYPES = [
    ('KEYWORD', r'\b(int|double|float|char|return|if|else|while|for)\b'),
    ('IDENTIFIER', r'\b[a-zA-z_][a-zA-Z0-9_]*\b'),
    ('BINARY_LITERAL', r'0[0b][01]+'),
    ('OCTAL_LITERAL', r'0[0o]?[0-7]+'),
    ('DECIMAL_LITERAL', r'\b\d+\b'),
    ('NUMBER', r'\d+'),
    ('INTEGER_LITERAL', r'\b\d+\b'),
    ('FLOATING_POINT_LITERAL', r'\b\d+\.\d+\b'),
    ('STRING_LITERAL', r'"(?:[^"\\]|\\.)*"'),
    ('CHARACTER_LITERAL', r"'(?:[^'\\]|\\.)'"),
    ('ARTHIMETIC_OPERATOR', r'[\+\-\*\/]+'),
    ('ASSIGNMENT_OPERATOR', r'[=]'),
    ('LOGICAL_OPERATOR', r'[\b(?:and|or|not)\b|&&|\|'),
    ('COMPARISON_OPERATOR', r'[<>]=?|==|!='),
    ('PUNCTUATION', r'[.;]'),
    ('WHITESPACE', r'\s+'),
    ('SINGLE_LINE_COMMENT', r'//[^\n]*'),
    ('MULTI_LINE_COMMENT', r'/\*[\s\S]*?\*/'),
]

class Lexer:
    def __init__(self, rules):

        # Applying a set of rules to the lexer
        self.rules = [(re.compile(pattern), token_type) for pattern, token_type in TOKEN_TYPES]

    
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
                    tokens.append((tokenText, tokenType, lineNum, columnNum))

                    # Updating the index
                    index = match.end(0)

                    #Calculating the length of the token
                    length = tokenText.splitlines()
                    if len(length) > 1:
                        lineNum += len(length) - 1
                        columnNum = len(length[-1]) + 1
                    else:
                        columnNum += tokenLength
                    break
          
            # Catching unsupported Grammar
            if not match:

                if index < len(text):
                    errorChar = text[index]
                else:
                    # Else, End of File reached
                    errorChar = '<EOF>'

                print(f"Position: {index}, Line number: {lineNum}, Column number: {columnNum}")
                raise SyntaxError(f"Unexpected character: {text[index]} at line {lineNum}, column {columnNum}")
              
    return tokens

