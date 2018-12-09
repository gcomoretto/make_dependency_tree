#!/usr/bin/env python
# take a list of pkgs and corresponding dependencies  (output from github-tree)
# and build a denendency tree
#  - direct dependencies that are already resolved indirectly are removed.
# the output is a dot file and the corresponding jpg
from __future__ import print_function
from operator import itemgetter
import argparse
import csv
import re
import os
from subprocess import call


def readFile(fin):
    # read pkgs from fin
    # sort pkgs, no deps first
    count = 0
    pkgs = {}
    lp = {}
    opkgs = {}
    
    for line in fin:
        line = line.strip()
        sline = line.split(':')
        if sline[1] == '':
            pkgs[ sline[0] ] = []
        else:
            pkgs[ sline[0] ] = sline[1].strip().split(', ')
        #lp [ sline[0] ] = len(pkgs[ sline[0] ])

    #for k, v in sorted(lp.items(), key = itemgetter(1), reverse = False):
    #    #print(k, v)
    #    opkgs[ k ] = pkgs[ k ]

    return(pkgs)

def check_indirect(cv, values):
    global pkgs
    found = False
    #print(' Check indirect dependecies', cv, ' on ', values)
    for v in values:
        v = v.strip()
        d = pkgs[ v ]
        #print('   -  ', v, d)
        if len(d)>0:
            if cv in d:
                #print('------------------------------ found it!')
                return(True)
            else:
                #print('--------------- looking in dependencies..')
                found = check_indirect(cv, d)
                if found:
                    return(found)

    return(found)

def do_dot_jpg(deps, fn):
    #
    print(' .. saving dot file and generating jpg')
   
    dotf = fn + '.dot'
    jpgf = fn + '.jpg'

    F=open(dotf, "w")
    F.write("graph G {\n")
    F.write("    node [shape=box];\n")
    for k, v in deps.items():
       if len(v)!=0:
          for e in v:
              F.write('    "' + e + '" -- "' + k + '";\n')
    F.write("}\n")
    F.close()
    call(["dot", "-Tjpg", "-o"+jpgf, dotf])


def do_tex_pdf(deps, fn):
    #
    print(' .. saving tex file and generating pdf')

    dotf = fn + '.dot'
    jpgf = fn + '.jpg'


def doFile(inFile):
    # 
    print('Input file', inFile)
    global pkgs

    pkgs = {}
    deps = {}

    with open(inFile) as fin:
        pkgs = readFile(fin)
    fin.close()

    for k, values in pkgs.items():
        #print(k)
        deps[ k ] = []
        for v in values:
            # for each dependency resolved directly, I need to check if it is also resolved
            #  by any other dependency
            odd = [x for x in values if x != v] # other direct deps
            v = v.strip()
            is_indirect = check_indirect(v, odd)
            if is_indirect==False:
                deps[ k ].append(v)
            #print(' - ', v, '<--', k)

    tmpFn=os.path.basename(inFile)
    sf = tmpFn.split('.')
    print('Output files', sf[0], '(.dot, .jpg, .tex, .pdf)')

    do_dot_jpg(deps, sf[0])
    #do_tex_pdf(deps, sf[0])

    #for k, values in deps.items():
    #    print(k, values)

# MAIN
parser = argparse.ArgumentParser()
parser.add_argument("--file", help="Input file ", default='lsst_distrib.pkg.txt')
args = parser.parse_args()
inp=args.file
doFile(inp)
