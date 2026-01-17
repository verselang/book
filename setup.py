#!/usr/bin/env python3
"""
Setup script for Verse lexer Pygments plugin
"""
from setuptools import setup, find_packages

setup(
    name='verse-lexer',
    version='1.0.0',
    packages=['verse_lexer'],
    entry_points={
        'pygments.lexers': [
            'verse = verse_lexer:VerseLexer',
        ],
    },
    install_requires=[
        'pygments>=2.16',
    ],
    description='Verse language lexer for Pygments',
    author='Verse Documentation Team',
    python_requires='>=3.8',
)
