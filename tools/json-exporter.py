#!/usr/bin/env python
# -*- coding: utf-8 -*-

from optparse import OptionParser
import fnmatch
import os
import sys
import re

from pprint import pprint
import ply.lex as lex

WINDOWS_LINE_ENDING = '\r\n'
UNIX_LINE_ENDING = '\n'

# List of token names.   This is always required
tokens = (
  'EQUAL',
  'LBRACKET',
  'RBRACKET',
  'LT',
  'GT',
  'COMMENT',
  'STRING',
  'NUMBER',
  'QUOTED_STRING'
)

def MyLexer():
    # Regular expression rules for simple tokens
    t_EQUAL      = r'='
    t_LBRACKET   = r'{'
    t_RBRACKET   = r'}'
    t_LT         = '<'
    t_GT         = '>'
    t_COMMENT    = r'\#.*'
    t_STRING     = r'[A-Za-z_]+'

    def t_QUOTED_STRING(t):
        r'\"([^\\\"]|\\.)*\"'
        t.value = t.value[1:-1]
        return t

    # A regular expression rule with some action code
    def t_NUMBER(t):
        r'[-\d\.]+'
        t.value = float(t.value)    
        return t

    # Define a rule so we can track line numbers
    def t_newline(t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    # A string containing ignored characters (spaces and tabs)
    t_ignore  = ' \t'

    # Error handling rule
    def t_error(t):
        print("Illegal character '%s'" % t.value[0])
        print("'%s'" % t.value[0])
        print(t.value[0])
        t.lexer.skip(1)

    # Build the lexer from my environment and return it    
    return lex.lex()

def open_crlf_lf(in_file):
    #try:
    with open(in_file, "r") as fh:
        return fh.read().replace(WINDOWS_LINE_ENDING, UNIX_LINE_ENDING)
    #except Exception as e:
    #    print("failed to open file %s" % in_file)
    #    sys.exit(1)

def analyze_file(in_file, data):
    lexer = MyLexer()
    lexer.input(open_crlf_lf(in_file))
    while True:
        tok = lexer.token()
        if not tok:
            break
        print(tok)


def main():

    parser = OptionParser()
    parser.add_option("-d", "--directory", dest="directory",
            help="directory containing the data files of hoi4",
            metavar="DIR")
    parser.add_option("-f", "--file", dest="file",
            help="path to a data file of hoi4 (ex: infantry.txt)",
            metavar="DIR")

    (options, args) = parser.parse_args()

    if options.directory is None and options.file is None:
        print("missing --directory or --file option")
        sys.exit(1)
    

    if options.file is not None and options.directory is not None:
        print("option --directory and --file are exclusive, please pick one")
        sys.exit(1)

    data = {}

    if options.file:
        analyze_file(options.file, data)

    if options.directory:
        matches = []
        for root, dirnames, filenames in os.walk(options.directory):
            for filename in fnmatch.filter(filenames, '*.txt'):
                if not re.match(r'.*names.*', root):
                    matches.append(os.path.join(root, filename))

        for in_file in matches:
            print(in_file)
            analyze_file(str(in_file), data)


if __name__ == '__main__':
    main()
