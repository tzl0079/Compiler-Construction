# Author: Thomas Lander
# Date: 11/08/24
# lexer.py

import re

# Credit to these websites for help: https://regexr.com/, and https://github.com/c-testsuite/c-testsuite for test files

# My Grammar:
TOKEN_TYPES = [
    (r'\b(auto|break|case|char|const|continue|default|do|double|else|enum|extern|float|for| \
     goto|if|inline|int|long|register|restrict|return|short|signed|sizeof|static|struct| \
     switch|typedef|union|unsigned|void|volatile|while)\b', 'KEYWORD'),
    (r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', 'IDENTIFIER'),
    (r'0b[01]+', 'BINARY_LITERAL'),
    (r'0o?[0-7]+', 'OCTAL_LITERAL'),
    (r'0x[0-9a-fA-F]+', 'HEX_LITERAL'),
    (r'\b\d+\.\d+\b', 'FLOATING_POINT_LIT'),
    (r'\b\d+\b', 'INTEGER_LITERAL'),
    (r'"(?:[^"\\]|\\.)*"', 'STRING_LITERAL'),
    (r"'(?:[^'\\]|\\.)'", 'CHARACTER_LITERAL'),
    (r'\+\+', 'INCREMENT_OPERATOR'), 
    (r'--', 'DECREMENT_OPERATOR'),
    (r'[\+\-\*\/\%]+', 'ARITHMETIC_OPERATOR'),
    (r'[=]', 'ASSIGNMENT_OPERATOR'),
    (r'\b(?:and|or|not|&&|\|)\b', 'LOGICAL_OPERATOR'),
    (r'[<>]=?|==|!=', 'COMPARISON_OPERATOR'),
    (r'[.;(){}]', 'PUNCTUATION'),
    (r'\s+', 'WHITESPACE'),
    (r'//[^\n]*', 'SINGLE_LINE_COMMENT'),
    (r'/\*[\s\S]*?\*/', 'MULTI_LINE_COMMENT'),
]


class Lexer:
    # Initializing the lexer
    def __init__(self, rules):
        self.rules = [(re.compile(pattern), token_type) for pattern, token_type in TOKEN_TYPES]

    # Tokenizing Function
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

                    # Ignoring Whitespace
                    if tokenType not in {'WHITESPACE', 'SINGLE_LINE_COMMENT', 'MULTI_LINE_COMMENT'}:
                        tokens.append((tokenText, tokenType, lineNum, columnNum))

                    # Updating index, lineNum, and columnNum
                    index = match.end(0)
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

