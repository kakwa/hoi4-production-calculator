#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from optparse import OptionParser
import fnmatch
import os
import sys
import re
import json

from pprint import pprint
import ply.lex as lex
import ply.yacc as yacc

WINDOWS_LINE_ENDING = '\r\n'
UNIX_LINE_ENDING = '\n'

# List of token names.
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

def merge_two_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z

# merge two dicts together up to a depth of 2 (dict of dict merge)
# TODO will crash and burn if "z[i]" is not a dictionary
def merge_two_dicts_depth2(x,y):
    z = x.copy()   # start with x's keys and values
    for i in y:
        if i not in z:
            z[i] = y[i]
        else:
            for j in y[i]:
                z[i][j] = y[i][j]
    return z


# content example
#
# stuff = {
#         foo = {
#             biture = sanglier
#             cost = 0.42
#             power > 9000
#             chance < 13.5
#             modifier = -0.7
#         }
#         bar = {
#             item1
#             item2
#             "item3 with quote"
#         }
#
# }

def Hoi4Lexer():

    # Regular expression rules for simple tokens
    t_EQUAL      = r'='
    t_LBRACKET   = r'{'
    t_RBRACKET   = r'}'
    t_LT         = '<'
    t_GT         = '>'
    t_STRING     = r'[A-Za-z0-9_]+'

    # matching for quoted string (only works if string is on one line)
    def t_QUOTED_STRING(t):
        r'\"([^\\\"]|\\.)*\"'
        t.value = t.value[1:-1]
        return t

    # matching for numbers
    def t_NUMBER(t):
        r'[-\d\.]+'
        if '.' in t.value:
            t.value = float(t.value)
        else:
            t.value = int(t.value)
        return t

    def t_newline(t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    t_ignore  = ' \t'

    def t_error(t):
        print("Illegal character '%s'" % t.value[0])
        print("'%s'" % t.value[0])
        print(t.value[0])
        t.lexer.skip(1)

    # Build the lexer from my environment and return it
    return lex.lex()

def Hoi4Yaccer():

    Hoi4Lexer()

    # match for stuff = <SOMETHING>
    def p_allocation(p):
        '''allocation : STRING EQUAL STRING
                      | STRING EQUAL list
                      | STRING EQUAL dict
                      | STRING EQUAL NUMBER
                      | STRING GT NUMBER
                      | STRING LT NUMBER
                      | STRING EQUAL QUOTED_STRING
        '''
        if p[2] == '=':
            p[0] = {p[1]: p[3]}
        else:
            # paradox format allows for inequalities, which doesn't map cleanly into json
            # but these are pretty rare (seen only for radar and sonar slots count on ships)
            # so we put them in a special format
            p[0] = {p[1]: {'operation': p[2], 'value': p[3]}, 'META': 'INEQ'}

    # match for { stuff1 stuff2 stuff3 }
    def p_list(p):
        '''list : LBRACKET string_items RBRACKET
        '''
        p[0] = p[2]

    # match for { }
    def p_empty_list(p):
        "list : LBRACKET RBRACKET"
        p[0] = []

    # match for 'stuff1 stuff2 stuff3' (content of { stuff1 stuff2 stuff3 })
    def p_elements(p):
        '''string_items : STRING string_items
                        | QUOTED_STRING string_items
        '''
        p[2].append(p[1])
        p[0] = p[2]

    # termination for previous
    def p_element_single(p):
        '''string_items : STRING
                        | QUOTED_STRING
        '''
        p[0] = [p[1]]

    # match for:
    # {
    #    stuff1 = <SOMETHING>
    #    stuff2 = <SOMETHING_ELSE>
    # }
    def p_dict(p):
        '''dict : LBRACKET allocation_items RBRACKET'''
        p[0] = p[2]

    # match for content of previous:
    #    stuff1 = <SOMETHING>
    #    stuff2 = <SOMETHING_ELSE>
    def p_allocation_items(p):
        '''allocation_items : allocation allocation_items'''
        p[0] = merge_two_dicts(p[1], p[2])

    # termination of previous
    def p_allocation_single(p):
        '''allocation_items : allocation'''
        p[0] = p[1]

    def p_error(p):
        print("Syntax error at '%s'" % p.value)

    return yacc.yacc()

def open_crlf_lf(in_file):
    with open(in_file, "r") as fh:
        # we replace CRLF by CF and remove comments
        return re.sub(r'#.*', '', fh.read().replace(WINDOWS_LINE_ENDING, UNIX_LINE_ENDING))

# debug function to visualize the tokenization
def _lex_file(in_file, data):
    lexer = Hoi4Lexer()
    lexer.input(open_crlf_lf(in_file))
    while True:
        tok = lexer.token()
        if not tok:
            break
        print(tok)

# parse a file and return a dictionnary
def analyze_file(in_file):
    parser = Hoi4Yaccer()
    print("analyzing file '%s'" % in_file)
    return parser.parse(open_crlf_lf(in_file))



# extract the bites that interest us for the production optimizer
def filter_data(data):
    ret = {'unit': {}, 'support': {}, 'equipement': {}}

    archetype_list = set([])

    # scan units
    for s in data['sub_units']:
        if 'group' in data['sub_units'][s]:
            if data['sub_units'][s]['group'] == 'support':
                ret['support'][s] = {
                    'need': data['sub_units'][s]['need']
                }
            else:
                ret['unit'][s] = {
                    'need': data['sub_units'][s]['need']
                }
            for a in data['sub_units'][s]['need']:
                archetype_list.add(a)

    # scan for equipement
    archetype_list2 = set([])
    for s in data['equipments']:
        equipement = data['equipments'][s]
        if 'archetype' in equipement and \
            equipement['archetype'] in archetype_list and \
            'year' in equipement:
                year = equipement['year']
                archetype = equipement['archetype']
                if 'build_cost_ic' in equipement:
                    build_cost_ic = equipement['build_cost_ic']
                else:
                    build_cost_ic = data['equipments'][archetype]['build_cost_ic']

                if year not in ret['equipement']:
                    ret['equipement'][year] = {}
                ret['equipement'][year][archetype] = {'cost': float(build_cost_ic)}
                archetype_list2.add(archetype)

    if archetype_list2 != archetype_list:
        raise Exception("failed to recover all the equipement types")
    return ret

def main():

    parser = OptionParser()
    parser.add_option("-d", "--directory", dest="directory",
            help="directory containing the data files of hoi4",
            metavar="DIR")
    parser.add_option("-f", "--file", dest="file",
            help="path to a data file of hoi4 (ex: infantry.txt)",
            metavar="DIR")
    parser.add_option("-o", "--out", dest="out_file",
            help="path of outpout json file", default=None,
            metavar="OUT")

    parser.add_option("-F", "--filter",
            action="store_true", dest="filtered", default=False,
            help="Filter and reorganize the json file to structure only the relevant data that interest us")

    (options, args) = parser.parse_args()

    if options.directory is None and options.file is None:
        print("missing --directory or --file option")
        sys.exit(1)


    if options.file is not None and options.directory is not None:
        print("option --directory and --file are exclusive, please pick one")
        sys.exit(1)

    data = {}

    if options.file:
        ret = analyze_file(options.file)
        data = merge_two_dicts_depth2(data, ret)

    if options.directory:
        matches = []
        for root, dirnames, filenames in os.walk(options.directory):
            for filename in fnmatch.filter(filenames, '*.txt'):
                if not re.match(r'.*names.*', root):
                    matches.append(os.path.join(root, filename))

        for in_file in matches:
            ret = analyze_file(str(in_file))
            data = merge_two_dicts_depth2(data, ret)

    if options.filtered:
        data = filter_data(data)

    json_data = json.dumps(data, sort_keys=True, indent=2, separators=(',', ': '))

    if options.out_file:
        with open(options.out_file, 'w') as o:
            o.write(json_data)
    else:
        print(json_data)

if __name__ == '__main__':
    main()
