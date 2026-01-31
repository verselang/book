"""
    pygments.lexers.verse
    ~~~~~~~~~~~~~~~~~~~~~

    Lexer for the Verse programming language.

    :copyright: Copyright 2006-2025 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import re
from pygments.lexer import RegexLexer, include, bygroups, words, default
from pygments.token import Text, Comment, Operator, Keyword, Name, String, \
    Number, Punctuation, Whitespace

__all__ = ['VerseLexer']


class VerseLexer(RegexLexer):
    """
    Lexer for the Verse programming language.

    Verse is a functional logic programming language developed by Epic Games
    for use in Fortnite Creative and UEFN (Unreal Editor for Fortnite).
    """

    name = 'Verse'
    url = 'https://dev.epicgames.com/documentation/en-us/uefn/verse-language-reference'
    aliases = ['verse']
    filenames = ['*.verse']
    mimetypes = ['text/x-verse', 'application/x-verse']
    version_added = '2.20'

    flags = re.MULTILINE | re.DOTALL

    # Specifier keywords that appear in angle brackets
    specifiers = (
        'abstract', 'computes', 'constructor', 'private', 'public', 'protected',
        'final', 'decides', 'inline', 'native', 'override', 'suspends', 'transacts',
        'internal', 'reads', 'writes', 'allocates', 'scoped', 'converges',
        'castable', 'concrete', 'unique', 'final_super', 'open', 'closed',
        'native_callable', 'module_scoped_var_weak_map_key', 'epic_internal',
        'persistable'
    )

    # Block-forming keywords (can be followed by :)
    block_keywords = (
        'if', 'then', 'else', 'for', 'block', 'loop', 'array', 'case'
    )

    # Data structure keywords
    data_structure_keywords = (
        'module', 'interface', 'class', 'struct', 'enum'
    )

    # Declaration keywords
    decl_keywords = (
        'var', 'set', 'using'
    )

    # Type keywords
    type_keywords = (
        'int', 'float', 'string', 'logic', 'char', 'any', 'void',
        'option', 'comparable', 'rational', 'tuple', 'type'
    )

    # Reserved words
    reserved_words = (
        'do', 'while', 'break', 'return', 'yield', 'spawn', 'sync',
        'race', 'branch', 'Self', 'where', 'continue'
    )

    # Logical operator keywords
    logical_operators = (
        'and', 'or', 'not'
    )

    tokens = {
        'root': [
            # Whitespace and newlines
            (r'\s+', Whitespace),

            # Comments
            (r'#[^\n]*', Comment.Single),
            (r'<#', Comment.Multiline, 'multiline-comment'),

            # Using statements
            (r'(using)(\s*)(\{)', bygroups(Keyword.Namespace, Whitespace, Punctuation), 'using-block'),

            # Specifiers in angle brackets
            (r'<(' + '|'.join(specifiers) + r')(\{[^}]*\})?>', Name.Decorator),

            # Data structure declarations (direct syntax)
            (r'\b(' + '|'.join(data_structure_keywords) + r')(\s+)([a-zA-Z_]\w*)',
             bygroups(Keyword, Whitespace, Name.Class)),

            # Function declarations
            (r'\b([a-zA-Z_]\w*)(\s*)(<[^>]+>)?(\s*)(\()',
             bygroups(Name.Function, Whitespace, Name.Decorator, Whitespace, Punctuation)),

            # Keywords
            (words(block_keywords, suffix=r'\b'), Keyword),
            (words(data_structure_keywords, suffix=r'\b'), Keyword),
            (words(decl_keywords, suffix=r'\b'), Keyword.Declaration),
            (words(type_keywords, suffix=r'\b'), Keyword.Type),
            (words(reserved_words, suffix=r'\b'), Keyword.Reserved),
            (words(logical_operators, suffix=r'\b'), Operator.Word),

            # Boolean constants
            (r'\b(true|false)\b', Keyword.Constant),

            # Numeric literals
            (r'0b[01_]+', Number.Bin),
            (r'0o[0-7_]+', Number.Oct),
            (r'0x[0-9a-fA-F_]+', Number.Hex),
            (r'[0-9]+\.[0-9]*([eE][+-]?[0-9]+)?', Number.Float),
            (r'\.[0-9]+([eE][+-]?[0-9]+)?', Number.Float),
            (r'[0-9]+([eE][+-]?[0-9]+)', Number.Float),
            (r'[0-9][0-9_]*', Number.Integer),

            # String literals
            (r'"', String.Double, 'string-double'),
            (r"'(\\\\|\\[^\\]|[^'\\])*'", String.Single),

            # Operators
            (r':=', Operator),  # Definition operator
            (r'=>', Operator),  # Lambda arrow
            (r'->', Operator),  # For loop arrow
            (r'\.\.', Operator),  # Range operator
            (r'[+\-*/]?=', Operator),  # Assignment operators
            (r'==|!=|<=|>=|<|>', Operator),  # Comparison operators
            (r'[+\-*/%]', Operator),  # Arithmetic operators
            (r'[?:]', Operator),  # Ternary and type annotation

            # Punctuation
            (r'[{}\[\](),;.]', Punctuation),

            # Qualified access (super:)
            (r'\(([a-zA-Z_]\w*):\)', Name.Builtin.Pseudo),

            # Decorators
            (r'@[a-zA-Z_]\w*', Name.Decorator),

            # Identifiers (must come after keywords)
            (r'[a-zA-Z_]\w*', Name),
        ],

        'multiline-comment': [
            (r'<#', Comment.Multiline, '#push'),  # Nested comment
            (r'#>', Comment.Multiline, '#pop'),    # End comment
            (r'[^<#]+', Comment.Multiline),        # Comment content
            (r'[<#]', Comment.Multiline),          # Single < or #
        ],

        'using-block': [
            (r'\s+', Whitespace),
            (r'/', Punctuation),                    # Path separator
            (r'[a-zA-Z_]\w*', Name.Namespace),      # Package name component
            (r'\.', Punctuation),                   # Dot in package names
            (r',', Punctuation),
            (r'\}', Punctuation, '#pop'),
        ],

        'string-double': [
            (r'<#', Comment.Multiline, 'multiline-comment'), # Comments are allowed inside strings
            (r'\{', String.Interpol, 'interpolation'),
            (r'[^"\\{<]+', String.Double),
            (r'"', String.Double, '#pop'),
        ],

        'interpolation': [
            (r'\}', String.Interpol, '#pop'),
            include('root'), 
        ],
    }

    def analyse_text(text):
        """Verse code detection heuristics."""
        score = 0.0

        # Check for Verse-specific keywords
        if re.search(r'\busing\s*\{.*\}', text):
            score += 0.3
        if re.search(r':=', text):
            score += 0.2
        if re.search(r'<(public|private|override|suspends|decides)>', text):
            score += 0.3
        if re.search(r'\b(spawn|race|sync)\s*[:{]', text):
            score += 0.2
        if re.search(r'\bclass\s*\(.*\)\s*:', text):
            score += 0.2
        if re.search(r'<#.*#>', text, re.DOTALL):
            score += 0.1

        return min(score, 1.0)